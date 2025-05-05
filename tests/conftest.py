# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import pytest
from invenio_app.factory import create_app as invenio_create_app


@pytest.fixture(scope="module")
def app_config(app_config: dict):
    """Expand default app-config."""
    app_config["THEME_FRONTPAGE"] = False
    return app_config


@pytest.fixture(scope="module")
def create_app():
    """Flask app fixture for invenio_edugain."""
    return invenio_create_app
