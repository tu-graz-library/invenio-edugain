# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask-extension setup for invenio-edugain."""

from flask import Flask

from . import config


class InvenioEdugain:
    """invenio-edugain flask-extension."""

    def __init__(self, app: Flask | None = None) -> None:
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["invenio-edugain"] = self

    def init_config(self, app: Flask) -> None:
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("EDUGAIN_"):
                app.config.setdefault(k, getattr(config, k))

        pysaml2_config = app.config["EDUGAIN_PYSAML2_CONFIG"]
        if signing_key := app.config.get("EDUGAIN_SIGNING_KEY"):
            pysaml2_config["key_file"] = signing_key
        if signing_cert := app.config.get("EDUGAIN_SIGNING_CRT"):
            pysaml2_config["cert_file"] = signing_cert

        encryption_config = pysaml2_config["encryption_keypairs"]
        if encryption_key := app.config.get("EDUGAIN_ENCRYPTION_KEY"):
            encryption_config["key_file"] = encryption_key
        if encryption_cert := app.config.get("EDUGAIN_ENCRYPTION_CRT"):
            encryption_config["cert_file"] = encryption_cert
