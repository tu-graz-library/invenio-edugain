# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utils for building configs."""

from flask import Flask
from flask.app import BuildError
from uritools import uricompose, urisplit


type JSON = str | int | float | bool | None | dict[str, JSON] | list[JSON]


def url_for_server(app: Flask, server_name: str | None, endpoint: str) -> str:
    """Generate a URL using `app`'s url_map, but build for `server_name`.

    This follows what flask.url_for does when no app_ctx nor request_ctx is pushed,
    except that it replaces app.config['SERVER_NAME'] with passed `server_name` instead.

    this builds both, relative and absolute URLs
    a server_name is considered relative when:
      - is `None`
      - starts with `./`
      - starts with `/`, but not with `//`
    a server_name is considered absolute when:
      - starts with a scheme (e.g. `https:`)
      - starts with `//` (`//` denotes that the thing after is a domain)
      - starts with anything but `/` or `./`
    """
    scheme = None
    script_name = None
    server_name_without_scheme = ""  # flask needs server_name without scheme
    want_absolute_url = False
    if server_name is None:
        server_name_without_scheme = ""
        want_absolute_url = False
    elif server_name.startswith("//"):
        server_name_without_scheme = server_name[2:]  # strip leading `//`
        want_absolute_url = True
    elif server_name.startswith(("/", "./")):
        server_name_without_scheme = ""
        script_name = server_name
        want_absolute_url = False
    elif (split_server_name := urisplit(server_name)).scheme:
        scheme = split_server_name.getscheme()
        server_name_without_scheme = uricompose(
            scheme=None,
            authority=split_server_name.getauthority(),
            path=split_server_name.getpath(),
            query=split_server_name.getquery(),
            fragment=split_server_name.getfragment(),
        )
        if split_server_name.authority:
            # when an authority was parsed, uricompose's result starts with `//`
            # flask requires this to be gone instead
            server_name_without_scheme = server_name_without_scheme[2:]
        want_absolute_url = True
    else:
        server_name_without_scheme = server_name
        want_absolute_url = True

    # if server_name has characters other than `/`, flask additionally requires no trailing `/`
    if server_name_without_scheme.strip("/"):
        server_name_without_scheme = server_name_without_scheme.rstrip("/")
    url_adapter = app.url_map.bind(
        server_name=server_name_without_scheme,
        script_name=script_name,
        url_scheme="https",
    )
    try:
        return url_adapter.build(
            endpoint=endpoint,
            force_external=want_absolute_url,
            url_scheme=scheme,
        )
    except BuildError as error:
        return app.handle_url_build_error(
            error=error,
            endpoint=endpoint,
            values={
                "_anchor": None,
                "_method": None,
                "_scheme": None,
                "_external": None,
            },
        )
