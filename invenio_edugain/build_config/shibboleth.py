# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Build configuration for shibboleth-eds."""

import re
from typing import TypedDict, Unpack

from flask import Flask

from .utils import JSON, url_for_server


class ShibbolethEDSKwargs(TypedDict, total=False):
    """TypedDict of values available for shibboleth-eds config.

    For further info on these see:
    - idpselect_config.js in this package, which sets defaults for these fields
    - online docs on shibboleth EDS configuration options
    """

    # allowableProtocols list[str] | None  # checks whether current URL's policy= query-param is contained in it, I recon this isn't needed
    alwaysShow: bool
    autoFollowCookie: str | None
    autoFollowCookieTTLs: list[int]
    autoFollowCookieProps: str | None
    best_ratio: float  # NOTE: must be set to math.log(ratio)
    dataSource: str  # NOTE: recommended to use `dataSources` instead
    dataSources: list[str]
    defaultLanguage: str
    defaultLogo: str
    defaultLogoHeight: int
    defaultLogoWidth: int
    defaultReturn: str
    defaultReturnIDParam: str
    doNotCollapse: bool
    extraCompareRegex: str | None  # NOTE: literal string, no regex expansion
    helpURL: str | None
    hiddenIdPs: list[str] | None
    # ie6Hack  # noone should need this anymore...
    ignoreKeywords: bool
    # ignoreURLParams  # always False, needed for redirect-after-login
    # insertAtDiv  # hard-coded instead
    langBundles: dict[
        str,
        dict[str, str],
    ]  # of form {'en': {'fatal.dicMissing': 'could not locate ...', ...}}
    maxHeight: int
    maxIdPCharsAltTxt: int
    maxIdPCharsButton: int
    maxIdPCharsDropDown: int
    maxPreferredIdps: int
    maxResults: int
    maxWdith: int
    minHeight: int
    minWidth: int
    myEntityID: str | None
    noWriteCookie: bool
    preferredIdP: list[str] | None
    redirectAllow: list[str] | None
    # returnWhiteList list[str] | None  # old name for redirectAllow
    samlIdPCookieTTL: int | None
    samlIdPCookieProps: str | None
    # selectedLanguage  # set by backend when building HTML instead
    setFocusTextBox: bool
    showListFirst: bool
    testGUI: bool


def build_shibboleth_eds_config(
    app: Flask,
    **kwargs: Unpack[ShibbolethEDSKwargs],
) -> dict[str, JSON]:
    """Build configuration for use with shibboleth-eds."""
    server_names: list[str] = []
    if server_name := app.config.get("SERVER_NAME"):
        server_names.append(server_name.rstrip("/"))
    if server_name := app.config.get("SITE_UI_URL"):
        server_names.append(server_name.rstrip("/"))
    if server_name := app.config.get("SITE_API_URL"):
        server_names.append(server_name.rstrip("/"))

    redirect_allow = []
    for server_name in sorted(set(server_names)):
        escaped_name = re.escape(server_name)
        # NOTE: used in javascript RegExp, without multiline flag
        redirect_allow.append(f"^{escaped_name}$")
        redirect_allow.append(f"^{escaped_name}/.*$")

    res = {
        "dataSource": url_for_server(
            app,
            server_name=None,  # construct relative URL, e.g. "/saml/discofeed"
            endpoint="invenio_edugain.disco_feed",
        ),
        "defaultReturn": url_for_server(
            app,
            server_name=app.config["SERVER_NAME"],
            endpoint="invenio_edugain.authn_request",
        ),
        "redirectAllow": redirect_allow,
        "ignoreURLParams": False,
    }

    return res | kwargs  # type: ignore[return-value]  # mypy can't tell that return type is correct
