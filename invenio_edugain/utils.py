# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utils for invenio-edugain."""

import enum
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from os import PathLike
from tempfile import NamedTemporaryFile
from typing import Any, Literal, Self, TypeGuard

import requests
import validators
from flask import current_app
from flask_security.registerable import register_user
from invenio_accounts.models import User, UserIdentity
from invenio_db import db
from invenio_oauthclient.utils import create_csrf_disabled_registrationform, fill_form
from OpenSSL.crypto import FILETYPE_PEM, load_certificate
from saml2 import BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.config import Config, SPConfig
from saml2.mdstore import InMemoryMetaData, MetadataStore
from saml2.response import AuthnResponse
from sqlalchemy import true
from uritools import uricompose, urisplit

from .models import IdPData


class _ABSENT(enum.Enum):
    """Sentinel distinguishable from `None`."""

    ABSENT = enum.auto()

    def __repr__(self) -> str:
        return "ABSENT"

    def __bool__(self) -> Literal[False]:
        return False


ABSENT = _ABSENT.ABSENT
type AbsentType = Literal[_ABSENT.ABSENT]

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


def location_is_remote(location: PathLike | str) -> TypeGuard[str]:
    """Check whether the given `location` is a local path or a remote URL."""
    # NOTE: remote locations need be of type str, so the isinstance-check is crucial.
    return isinstance(location, str) and validators.url(location)


def load_mdstore(
    metadata_xml_location: PathLike | str,
    cert_location: PathLike | str | None = None,
    fingerprint_sha256: str | None = None,
    *,
    http_client_timeout: int = 30,
) -> MetadataStore:
    """Load a pysaml2 MetadataStore from given path/url.

    When loading metadata from url, requires a certificate to check validity of metadata.
    When loading that certificate from url, requires a fingerprint to check validity of certificate.
    """
    mds = MetadataStore(None, Config(), http_client_timeout=http_client_timeout)

    if not location_is_remote(metadata_xml_location):
        mds.load("local", metadata_xml_location)
        return mds

    # load metadata from url: need cert, either via local cert-file or remote fingerprint-checked cert
    if cert_location is None:
        msg = "must provide a certificate when loading metadata-xml from URL"
        raise TypeError(msg)

    if not location_is_remote(cert_location):
        mds.load(
            "remote",
            url=metadata_xml_location,
            check_validity=True,
            cert=cert_location,
        )
        return mds

    # load cert from url: download cert and check fingerprint
    if fingerprint_sha256 is None:
        msg = "must provide a fingerprint when loading certificate from URL"
        raise TypeError(msg)

    response = requests.get(cert_location, timeout=http_client_timeout)
    response.raise_for_status()
    cert_bytes = response.content

    cert = load_certificate(FILETYPE_PEM, cert_bytes)
    calculated_fingerprint = cert.digest("SHA256").decode()
    if fingerprint_sha256 != calculated_fingerprint:
        msg = "downloaded cert's fingerprint didn't match"
        raise ValueError(msg)

    # mds.load requires `cert` to be a file-path, so write cert to a temporary file:
    with NamedTemporaryFile("wb", suffix=".pem") as temp_cert_buf:
        temp_cert_buf.write(cert_bytes)
        temp_cert_buf.flush()  # flush instead of closing, as OS might delete closed file...
        mds.load(
            "remote",
            url=metadata_xml_location,
            check_validity=True,
            cert=temp_cert_buf.name,
        )

    return mds


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
    additional_attributes: dict[str, list[str]]  # unrequested attributes sent by IdP
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
            "affiliations": ";".join(authn_info.affiliations),
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
        confirmed_at = datetime.now(UTC)
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


def secure_redirect_url(unsafe_url: str) -> str:
    """Create safe (local) redirect URL from potentially unsafe (remote) URL.

    This mirrors invenio_oauthclient.utils:get_safe_redirect_target,
    but with different arguments.
    """
    allowed_hosts = current_app.config.get("APP_ALLOWED_HOSTS") or []
    split_uri = urisplit(unsafe_url)
    if split_uri.host in allowed_hosts:
        # given url was safe after all...
        return unsafe_url
    if split_uri.path:
        return uricompose(
            # leave out scheme=..., and authority=... to compose a local uri
            path=split_uri.getpath(),
            query=split_uri.getquery(),
            fragment=split_uri.getfragment(),
        )
    if security_url := current_app.config.get("SECURITY_POST_LOGIN_VIEW"):
        return security_url

    return "/"
