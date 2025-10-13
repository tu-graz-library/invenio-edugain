# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Configuration for invenio-edugain."""

EDUGAIN_LOGIN_ENABLED = True

EDUGAIN_ROUTES = {
    "acs": "/acs",
    "authn-request": "/login/authn-request",
    "discofeed": "/discofeed",
    "login-discover": "/login/discover",
    "sp-xml": "/sp/xml",
}

# TODO: make configuration more convenient than writing the whole config-dict into this var
EDUGAIN_PYSAML2_CONFIG: dict[str, str | list | dict] = {}

EDUGAIN_SHIBBOLETH_EDS_CONFIG: dict[str, str | list | dict] = {}
