# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utils for invenio-edugain."""

from typing import Any

from invenio_db import db
from saml2.mdstore import InMemoryMetaData
from sqlalchemy import select, true

from .models import IdPData

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
