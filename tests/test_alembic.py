# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test alembic recipes for Invenio-pages."""

from flask import Flask
from invenio_db.shared import SQLAlchemy
from invenio_db.utils import alembic_test_context, drop_alembic_version_table


def test_alembic(base_app: Flask, db: SQLAlchemy) -> None:
    """Test alembic recipes."""
    ext = base_app.extensions["invenio-db"]

    base_app.config["ALEMBIC_CONTEXT"] = alembic_test_context()

    # Check that this package's SQLAlchemy models have been properly registered
    tables = list(db.metadata.tables)

    assert "edugain_idp_data" in tables

    # Check that Alembic agrees that there's no further tables to create.
    assert len(ext.alembic.compare_metadata()) == 0

    # Drop everything and recreate tables all with Alembic
    db.drop_all()
    drop_alembic_version_table()
    ext.alembic.upgrade()
    assert len(ext.alembic.compare_metadata()) == 0

    # Try to upgrade and downgrade
    ext.alembic.stamp()
    ext.alembic.downgrade(target="96e796392533")
    ext.alembic.upgrade()
    assert len(ext.alembic.compare_metadata()) == 0

    drop_alembic_version_table()
