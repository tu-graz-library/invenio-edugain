# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module for importing idp-data."""

from dataclasses import dataclass, field
from itertools import chain

from invenio_db import db
from saml2.mdstore import MetadataStore

from .models import IdPData


@dataclass
class IdPDataImportItem:
    """Holds information on import-work done."""

    added_idp_ids: list[str] = field(default_factory=list)
    unchanged_idp_ids: list[str] = field(default_factory=list)
    updated_idp_ids: list[str] = field(default_factory=list)


def pick_squarest_logo(mds: MetadataStore, idp_id: str, default: str = "") -> str:
    """Return logo-url with width/height ratio closest to 1."""
    pick = default
    best_ratio = 0.0
    for logo_dict in mds.mdui_uiinfo_logo(idp_id):
        url = logo_dict["text"]
        width = int(logo_dict["width"])
        height = int(logo_dict["height"])

        ratio = min(width, height) / max(width, height, 1)
        if ratio > best_ratio:
            pick = url
            best_ratio = ratio

    return pick


def from_mdstore(mds: MetadataStore) -> IdPDataImportItem:
    """Ingest idp-data from a pysaml2 MetadataStore object."""
    result_item = IdPDataImportItem()

    idp_ids: list[str] = sorted(mds.identity_providers())
    existing_idp_data: dict[str, IdPData] = {
        idp_data.id: idp_data for idp_data in db.session.scalars(db.select(IdPData))
    }
    for idp_id in idp_ids:
        # not all edugain-members provide mdui_uiinfo
        # therefore the generator `mds.mdui_uiinfo_display_name(...)` might be empty
        # chain with `mds.name(...)` as a fallback
        name_generator = chain(
            mds.mdui_uiinfo_display_name(idp_id),
            mds.name(idp_id),
        )
        displayname = next(name_generator)
        logo_url = pick_squarest_logo(mds, idp_id)
        settings = mds[idp_id]
        if idp_id in existing_idp_data:
            idp_data = existing_idp_data[idp_id]
            if (
                idp_data.displayname != displayname
                or idp_data.logo_url != logo_url
                or idp_data.settings != settings
            ):
                idp_data.displayname = displayname
                idp_data.logo_url = logo_url
                idp_data.settings = settings
                result_item.updated_idp_ids.append(idp_id)
            else:
                result_item.unchanged_idp_ids.append(idp_id)
        else:
            idp_data = IdPData(
                id=idp_id,
                displayname=displayname,
                logo_url=logo_url,
                settings=settings,
            )
            result_item.added_idp_ids.append(idp_id)
        db.session.add(idp_data)

    db.session.commit()

    return result_item
