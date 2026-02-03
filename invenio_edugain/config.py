# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Configuration for invenio-edugain."""

from .build_config import UninitializedConfig
from .build_config.shibboleth import ShibbolethEDSKwargs

EDUGAIN_ALLOW_IMGSRC_CSP: bool | None = None
"""Whether to allow dico-page to set the `imgsrc: *` content-security-policy.

NOTE: this potential CSP change only affects discovery-page
Since logos are hosted on their home-organization, this is necessary to load logo-imgs on discovery-page.
Since changes to CSP are security-relevant, we won't change it without this opt-in.
Since most people will want this, the default `None` raises an error.
"""

EDUGAIN_LOGIN_ENABLED = True

EDUGAIN_ROUTES = {
    "acs": "/acs",
    "authn-request": "/login/authn-request",
    "discofeed": "/discofeed",
    "login-discover": "/login/discover",
    "sp-xml": "/sp/xml",
}

#
# Configuration for pysaml2 and shibboleth-eds
#
pysaml2_config_error_msg = """config-var `EDUGAIN_PYSAML2_CONFIG` was never set
if you turned off automatic config-building, be sure to set it yourself"""
EDUGAIN_PYSAML2_CONFIG: dict[str, str | list | dict] | UninitializedConfig = (
    UninitializedConfig(ValueError(pysaml2_config_error_msg))
)
"""After app-finalization, this must be set to a dict loadable by `pysaml2.config:Config.load`.
You will usually want to build this using the machinery in `invenio_edugain.build_config`.
See pysaml2's "Configuration of PySAML2 entities" documentation for advanced configuration needs.
"""
EDUGAIN_PYSAML2_CONFIG_BUILDING_ENABLED: bool = True
"""Disable automatic config-building to configure yourself instead.
When configuring yourself, set your configuration to `app.config["EDUGAIN_PYSAML2_CONFIG"]`.
Feel free to use (parts of) the config-building-machinery in `invenio_edugain.build_config`.
"""

EDUGAIN_SHIBBOLETH_EDS_CONFIG: dict[str, str | list | dict] | None = None
"""After app-finalization, this must be set to a dict for use with shibboleth-EDS.
You will usually want to build this using the machinery in `invenio_edugain.build_config`.
See shibboleth's "EDS Configuration Options" documentation for advanced configuration needs.
See the bundled shibboleth-eds/idpselect_config.js for default values.
"""
EDUGAIN_SHIBBOLETH_EDS_CONFIG_BUILDING_ENABLED: bool = True
"""Disable automatic config-building to configure yourself instead.
When configuring yourself, set your configuration to `app.config["EDUGAIN_SHIBBOLETH_EDS_CONFIG"]`.
Feel free to use (parts of) the config-building-machinery in `invenio_edugain.build_config`.
"""
EDUGAIN_SHIBBOLETH_EDS_CONFIG_KWARGS: ShibbolethEDSKwargs | None = None
"""Provide additional kwargs for shibbleth-eds-config.
Only used in automatic config-building.
"""


EDUGAIN_DISCOVERY_CSS: str = "invenio-edugain-eds-less.css"
"""CSS used on discovery page (i.e. the *choose your institution to log in with* page ).
Set to configured webpack key.
"""
