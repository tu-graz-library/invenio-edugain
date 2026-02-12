# -*- coding: utf-8 -*-
#
# Copyright (C) 2025-2026 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio extension for login via edugain."""

from .ext import InvenioEdugain

__version__ = "0.2.1"

__all__ = (
    "InvenioEdugain",
    "__version__",
)
