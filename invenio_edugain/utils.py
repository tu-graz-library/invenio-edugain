# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utils for invenio-edugain."""

from invenio_db import db
from sqlalchemy import select, true

from .models import IdPData


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
