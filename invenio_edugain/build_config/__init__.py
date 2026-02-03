# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utils to build configurations for use with pysaml2 and shibboleth-eds."""

from .pysaml2 import build_pysaml2_config
from .pysaml2_core import (
    Pysaml2ConfigCore,
    Pysaml2ConfigCoreContacts,
    Pysaml2ConfigCoreCryptographicCredentials,
    Pysaml2ConfigCoreEntityCategories,
    Pysaml2ConfigCoreOrganization,
    Pysaml2ConfigCoreProvidedService,
    Pysaml2ConfigCoreUIInfo,
)
from .shibboleth import build_shibboleth_eds_config
from .utils import UninitializedConfig

__all__ = (
    "Pysaml2ConfigCore",
    "Pysaml2ConfigCoreContacts",
    "Pysaml2ConfigCoreCryptographicCredentials",
    "Pysaml2ConfigCoreEntityCategories",
    "Pysaml2ConfigCoreOrganization",
    "Pysaml2ConfigCoreProvidedService",
    "Pysaml2ConfigCoreUIInfo",
    "UninitializedConfig",
    "build_pysaml2_config",
    "build_shibboleth_eds_config",
)
