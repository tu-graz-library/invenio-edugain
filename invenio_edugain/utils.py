# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utils for invenio-edugain."""

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import TYPE_CHECKING, Any, Self

from flask import current_app
from flask_security.registerable import register_user
from invenio_accounts.models import User, UserIdentity
from invenio_db import db
from invenio_oauthclient.utils import create_csrf_disabled_registrationform, fill_form
from saml2 import BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.config import SPConfig
from saml2.mdstore import InMemoryMetaData
from sqlalchemy import select, true

from .models import IdPData

if TYPE_CHECKING:
    from saml2.response import AuthnResponse

NS_PREFIX = {
    "alg": "urn:oasis:names:tc:SAML:metadata:algsupport",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
    "eidas": "http://eidas.europa.eu/saml-extensions",
    "md": "urn:oasis:names:tc:SAML:2.0:metadata",
    "mdattr": "urn:oasis:names:tc:SAML:metadata:attribute",
    "mdui": "urn:oasis:names:tc:SAML:metadata:ui",
    "remd": "http://refeds.org/metadata",
    "saml2": "urn:oasis:names:tc:SAML:2.0:assertion",
    "saml2p": "urn:oasis:names:tc:SAML:2.0:protocol",
}
"""Names for namespaces that SAML commonly uses."""


# TODO: cache
def get_idp_data_dict() -> dict:
    """Get from db a dict of the IdP-data of *enabled* idps."""
    query = select(IdPData).where(IdPData.enabled == true())
    idps_data: list[IdPData] = db.session.execute(query).scalars()

    return {
        idp_data.id: {
            "displayname": idp_data.displayname,
            "logo_url": idp_data.logo_url,
        }
        for idp_data in idps_data
    }


class MetaDataFlaskSQL(InMemoryMetaData):
    """Loads idp-settings from SQL-db.

    This is akin to saml2.mdstore.MetaDataMD, which loads from file rather than from db.
    """

    def __init__(
        self,
        attrc: tuple | None,
        __: str,  # this loading run's id, always passed as a second positional arg
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Init."""
        super().__init__(attrc, **kwargs)

    def load(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401, ARG002
        """Load."""
        for idp in db.session.scalars(
            db.select(IdPData).where(IdPData.enabled == true()),
        ):
            self.entity[idp.id] = idp.settings


class AuthnResponseError(Exception):
    """Raised when authn response is incorrect somehow."""


@dataclass
class AuthnInfo:
    """Parsed authentication info."""

    id_by_method: dict[str, str | None]  # NOTE: ids hashed, preferred methods first
    additional_attributes: list[str]  # attributes the IdP sent despite us not asking
    affiliations: list[str]
    emails: list[str]  # potentially empty list
    full_name: str  # potentially empty string
    next: str | None
    user: User | None  # None iff no corresponding user exists (yet)
    username: str  # potentially empty string

    @classmethod
    def from_saml_response(  # noqa: C901, PLR0912
        cls,
        saml_xml_response: str,
        next_: str | None = None,
    ) -> Self:
        """Create authentication info from a saml xml."""
        config_dict = current_app.config["EDUGAIN_PYSAML2_CONFIG"]
        config = SPConfig()
        config.load(config_dict)
        client = Saml2Client(config)

        authn_response: AuthnResponse | None = client.parse_authn_request_response(
            saml_xml_response,
            BINDING_HTTP_POST,
        )
        if authn_response is None:
            msg = "error when parsing SAML <Response>"
            raise AuthnResponseError(msg)

        # ava (attribute value assertions) is dict: friendlyName->list[str]
        ava = authn_response.get_identity()

        id_by_method = {}
        for method in ("pairwise-id", "subject-id", "eduPersonPrincipalName"):
            ids = ava.pop(method, [])
            if len(ids) > 1:
                msg = f"SAML <Response> contained multiple {method}s"
                raise AuthnResponseError(msg)
            id_by_method[method] = ids[0] if ids else None

        # pairwise-id is only unique in combination with issuer, combine them
        if id_by_method["pairwise-id"]:
            issuer: str = authn_response.issuer()
            if not issuer:
                # saml-core-2.0 marks <Issuer> as required
                msg = "SAML <Response> didn't include mandatory <Issuer> field"
                raise AuthnResponseError(msg)
            id_by_method["pairwise-id"] = f'{issuer}!{id_by_method["pairwise-id"]}'

        # hash ids
        for method, id_ in list(id_by_method.items()):
            id_by_method[method] = sha256(id_.encode()).hexdigest() if id_ else None

        if all(id_ is None for id_ in id_by_method.values()):
            msg = "SAML <Response> contained no known kinds of identification"
            raise AuthnResponseError(msg)

        affiliations = ava.pop("eduPersonScopedAffiliation", [])
        displaynames = ava.pop("displayName", [])
        emails = ava.pop("mail", [])
        emails.extend(ava["email"])  # TODO: remove
        given_names = ava.pop("givenName", [])
        family_names = ava.pop("sn", [])

        fullname = (" ".join(given_names) + " " + " ".join(family_names)).strip()
        if displaynames:
            username = displaynames[0]
        elif emails:
            username = emails[0].split("@")[0]
        else:
            username = fullname

        first_found_user = None
        for method, id_ in id_by_method.items():
            if found_user := UserIdentity.get_user(method, id_):
                if first_found_user is None:
                    first_found_user = found_user
                elif first_found_user != found_user:
                    # muliple methods given, linking to different users
                    msg = "SAML <Response> identifies multiple different users"
                    raise AuthnResponseError(msg)

        return cls(
            id_by_method=id_by_method,
            additional_attributes=ava,
            affiliations=affiliations,
            emails=emails,
            full_name=fullname,
            next=next_,
            user=first_found_user,
            username=username,
        )


def create_user(authn_info: AuthnInfo) -> User:
    """Create user and link it with first method in authn_info.id_by_method.

    Returns a current_app.extension['security'].datastore.user_model instance of the created user.
    """
    if authn_info.user is not None:
        msg = "Tried to create a user when they already exist"
        raise ValueError(msg)

    # use first provided method of login
    method, external_id = next(
        (meth, id_) for meth, id_ in authn_info.id_by_method.items() if id_ is not None
    )
    user_dict = {
        "email": authn_info.emails[0],
        "profile": {
            "affiliations": "\n".join(authn_info.affiliations),
            "full_name": authn_info.full_name,
            "username": authn_info.username,
        },
    }

    # create new user
    form = create_csrf_disabled_registrationform("edugain")
    form = fill_form(
        form,
        user_dict,
    )
    if form.validate():
        # see invenio_saml.invenio_accounts.utils:account_register
        confirmed_at = datetime.now(timezone.utc)
        data = {
            **form.to_dict(),
            "confirmed_at": confirmed_at,
        }
        if not data.get("password"):
            data["password"] = ""
        user = register_user(**data)
        if not data["password"]:
            user.password = None
        current_app.extensions["security"].datastore.commit()
    else:
        msg = "form failed to validate when trying to create a user"
        raise AuthnResponseError(msg)

    UserIdentity.create(user, method=method, external_id=external_id)
    db.session.commit()

    return user
