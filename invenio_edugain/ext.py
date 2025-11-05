# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask-extension setup for invenio-edugain."""

from flask import Flask

from . import config
from .build_config import (
    Pysaml2ConfigCore,
    build_pysaml2_config,
    build_shibboleth_eds_config,
)


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


def finalize_app(app: Flask) -> None:
    """Finalize app."""
    setup_configuration(app)


def setup_configuration(app: Flask) -> None:
    """Automatic setup of configuration (insofar enabled)."""
    if app.config.get("EDUGAIN_PYSAML2_CONFIG_BUILDING_ENABLED", True):
        try:
            config_core = Pysaml2ConfigCore(flask_config=app.config)
            pysaml2_config = build_pysaml2_config(app=app, config_core=config_core)
        except Exception as exception:
            exception.add_note(
                "when automatically building pysaml2 config on startup\n"
                "automatic building can be turned off via `EDUGAIN_PYSAML2_CONFIG_BUILDING_ENABLED`.",
            )
            raise
        app.config["EDUGAIN_PYSAML2_CONFIG"] = pysaml2_config

    if app.config.get("EDUGAIN_SHIBBOLETH_EDS_CONFIG_BUILDING_ENABLED", True):
        shibboleth_kwargs = (
            app.config.get("EDUGAIN_SHIBBOLETH_EDS_CONFIG_KWARGS", {}) or {}
        )
        try:
            shibboleth_eds_config = build_shibboleth_eds_config(
                app,
                **shibboleth_kwargs,
            )
        except Exception as exception:
            exception.add_note(
                "when automatically building shibboleth-eds config on startup\n"
                "automatic building can be turned off via `EDUGAIN_SHIBBOLETH_EDS_CONFIG_BUILDING_ENABLED`.",
            )
            raise
        app.config["EDUGAIN_SHIBBOLETH_EDS_CONFIG"] = shibboleth_eds_config
