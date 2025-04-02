# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for invenio-edugain."""

import validators
from celery import shared_task
from saml2.config import Config
from saml2.mdstore import MetadataStore

from . import ingest


@shared_task
def ingest_idp_data(file_or_url: str) -> None:
    """Ingest idp-data from given SAML metadata XML into db."""
    mds = MetadataStore(None, Config())
    if validators.url(file_or_url):
        mds.load("remote", url=file_or_url)
    else:
        mds.load("local", file_or_url)

    ingest.from_mdstore(mds)
