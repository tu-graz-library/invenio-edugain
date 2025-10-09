# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS Webpack bundles for invenio-edugain."""

from invenio_assets.webpack import WebpackThemeBundle

edugain = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "aliases": {
                "@js/invenio_edugain": "js/invenio_edugain",
                "@js/shibboleth_eds": "shibboleth-embedded-ds-1.3.0/nonminimised",
            },
            "copy": {},
            "dependencies": {
                "jquery": "^3.2.1",
                "prop-types": "^15.7.2",
                "react": "^16.13.0",
                "react-dom": "^16.13.0",
            },
            "devDependencies": {},
            "entry": {
                "invenio-edugain-discovery": "./js/invenio_edugain/discovery.js",
            },
            "peerDependencies": {},
        },
    },
)
