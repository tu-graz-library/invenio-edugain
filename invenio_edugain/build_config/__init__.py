# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utils to build configurations for use with pysaml2 and shibboleth-eds."""

from .shibboleth import build_shibboleth_eds_config

__all__ = (
    "build_shibboleth_eds_config",
)
