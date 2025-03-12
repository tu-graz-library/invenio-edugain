# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test data ingestion."""

from invenio_db.shared import SQLAlchemy
from saml2.config import Config
from saml2.mdstore import MetadataStore

from invenio_edugain import ingest
from invenio_edugain.models import IdPData

# might as well test with real data...
EDUGAIN_XML_URL = "https://mds.edugain.org/edugain-v2.xml"


def test_data_ingestion(db: SQLAlchemy):
    """Test ingestion of idp-data from url."""
    mds = MetadataStore(None, Config())
    mds.load("remote", url=EDUGAIN_XML_URL)

    result_item = ingest.from_mdstore(mds)
    assert len(result_item.added_idp_ids) > 0
    assert len(result_item.unchanged_idp_ids) == 0
    assert len(result_item.updated_idp_ids) == 0

    result_item = ingest.from_mdstore(mds)
    assert len(result_item.added_idp_ids) == 0
    assert len(result_item.unchanged_idp_ids) > 0
    assert len(result_item.updated_idp_ids) == 0

    idp_datas = db.session.scalars(db.select(IdPData)).all()
    assert len(idp_datas) > 0
