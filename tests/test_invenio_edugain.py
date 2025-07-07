# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""


def test_version():
    """Test for existence of `__version__` attribute."""
    from invenio_edugain import __version__  # noqa: PLC0415

    assert __version__
