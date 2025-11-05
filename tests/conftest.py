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
    app_config["EDUGAIN_ALLOW_IMGSRC_CSP"] = True

    # automatic pysaml2-config building fails on app startup unless given a bunch of vars
    # one such necessary var is a path to an existing file, which is hard to emulate
    # disable instead
    app_config["EDUGAIN_PYSAML2_CONFIG_BUILDING_ENABLED"] = False

    # shibboleth-eds config is simpler and should be buildable anyway...
    app_config["EDUGAIN_SHIBBOLETH_EDS_CONFIG_BUILDING_ENABLED"] = True

    return app_config


@pytest.fixture(scope="module")
def create_app():
    """Flask app fixture for invenio_edugain."""
    return invenio_create_app
