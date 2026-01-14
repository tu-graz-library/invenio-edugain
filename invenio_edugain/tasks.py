# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for invenio-edugain."""

from celery import shared_task
from flask import current_app

from . import ingest
from .utils import load_mdstore


@shared_task
def ingest_idp_data(
    metadata_xml_location: str,
    cert_location: str | None = None,
    fingerprint_sha256: str | None = None,
) -> None:
    """Ingest idp-data from given SAML metadata XML into db."""
    mds = load_mdstore(metadata_xml_location, cert_location, fingerprint_sha256)
    item = ingest.from_mdstore(mds)

    log_msg = (
        f"succesfully ingested IdP data from {metadata_xml_location!r}:\n"
        f"{len(item.added_idp_ids)} added: {item.added_idp_ids!r},\n"
        f"{len(item.updated_idp_ids)} updated: {item.updated_idp_ids!r},\n"
        f"{len(item.unchanged_idp_ids)} unchanged: [...]"  # list of unchanged omitted for log brevity
    )
    current_app.logger.info(log_msg)
