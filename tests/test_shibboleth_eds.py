# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests concerning the vendored shibboleth-EDS."""

import re
from importlib.resources import files

import requests
from lxml.html import fromstring

LATEST_SHIBBOLETH_EDS_URL = (
    "https://shibboleth.net/downloads/embedded-discovery-service/latest"
)

SHIBBOLETH_EDS_UPGRADE_GUIDE = f"""upgrade guide:
- pull new version from {LATEST_SHIBBOLETH_EDS_URL}
- extract new version to invenio_edugain/assets/semantic-ui/
- delete unneeded files:
  - ./idpselect.js (the one in root of dir, which is minified already, but we use webpack to minify ourselves)
  - ./idselect_config.js (which is a copy of ./nonminimised/idpselect_config.js)
  - ./index.html (we use a jinja-template instead)
  - ./Makefile (instead done via webpack and assets-building)
  - ./shibboleth-ds.conf (unneeded hook-up into Apache Server)
  - ./shibboleth-embedded-ds.spec (unneeded hook-up into Apache Server)
  - ./nonminimised/json2.js (unneeded fallback implementation of javascript's JSON.parse)
- add legal headers to *.css and *.js files (see currently vendored version for how this looks like)
- format added *.js files with eslint+prettier using configuration in invenio_edugain/.eslintrc.yml
- add needed imports to *.js files (see currently vendored version)
- remove intialization code from bottom of ./nonminimised/idpselect.js (we initialize elsewhere)
- run eslint with invenio_edugain/.eslintrc as configuration and fix errors it finds
- merge <currently-vendored-eds>/nonminised/idpselect_languages.js and <new-eds>/nonminimised/idpselect_languages.js
  (vendored idpselect_languages.js might have been updated by PR, so new version's translated-strings aren't necessarily newer)
- retarget invenio_edugain/webpack.py to new version
- delete old version's files/directories
"""


def test_upgradable():
    """Test for newer versions of shibboleth-EDS."""
    vendored_dirs = list(files("invenio_edugain").rglob("shibboleth-embedded-ds-*"))
    if len(vendored_dirs) == 0:
        msg = "found no vendored `shibboleth-embedded-ds` of any version"
        raise ValueError(msg)
    if len(vendored_dirs) > 1:
        msg = "found multiple vendored `shibboleth-embedded-ds` versions"
        raise ValueError(msg)

    m = re.match("^shibboleth-embedded-ds-(.*)$", vendored_dirs[0].name)
    if not m:
        # shouldn't really happen given that we matched the above glob
        msg = "vendored `shibboleth-embedded-ds`'s name didn't match regex"
        raise ValueError(msg)
    vendored_version = m.group(1)

    response = requests.get(
        LATEST_SHIBBOLETH_EDS_URL,
        timeout=60,  # in seconds
    )
    response.raise_for_status()

    html_root = fromstring(response.content)
    latest_versions = [
        m.group(1)
        for a in html_root.xpath("body//a")
        if (m := re.match("^shibboleth-embedded-ds-(.*).tar.gz$", a.text))
    ]
    if len(latest_versions) == 0:
        msg = "found no latest `shibboleth-embedded-ds` version"
        raise ValueError(msg)
    if len(latest_versions) > 1:
        msg = "found multiple latest `shibboleth-embedded-ds` versions"
        raise ValueError(msg)
    latest_version = latest_versions[0]

    if vendored_version != latest_version:
        msg = (
            "a newer version of `shibboleth-embedded-ds` exists\n"
            "please upgrade the vendored version\n"
            "\n" + SHIBBOLETH_EDS_UPGRADE_GUIDE
        )
        raise ValueError(msg)
