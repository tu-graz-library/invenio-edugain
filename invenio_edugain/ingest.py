# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module for importing idp-data."""

from dataclasses import dataclass, field

from invenio_db import db
from saml2.mdstore import MetadataStore

from .models import IdPData


@dataclass
class IdPDataImportItem:
    """Holds information on import-work done."""

    added_idp_ids: list[str] = field(default_factory=list)
    unchanged_idp_ids: list[str] = field(default_factory=list)
    updated_idp_ids: list[str] = field(default_factory=list)


def from_mdstore(mds: MetadataStore) -> IdPDataImportItem:
    """Ingest idp-data from a pysaml2 MetadataStore object."""
    result_item = IdPDataImportItem()

    idp_ids: list[str] = sorted(mds.identity_providers())
    existing_idp_data: dict[str, IdPData] = {
        idp_data.id: idp_data for idp_data in db.session.scalars(db.select(IdPData))
    }
    for idp_id in idp_ids:
        settings = mds[idp_id]
        if idp_id in existing_idp_data:
            idp_data = existing_idp_data[idp_id]
            if idp_data.settings != settings:
                idp_data.settings = settings
                result_item.updated_idp_ids.append(idp_id)
            else:
                result_item.unchanged_idp_ids.append(idp_id)
        else:
            idp_data = IdPData(
                id=idp_id,
                settings=settings,
            )
            result_item.added_idp_ids.append(idp_id)
        db.session.add(idp_data)

    db.session.commit()

    return result_item
