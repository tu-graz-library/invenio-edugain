# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""invenio-edugain views."""

from flask import (
    Blueprint,
    Flask,
    abort,
    current_app,
    redirect,
    render_template,
    request,
)
from saml2.client import Saml2Client
from saml2.config import SPConfig
from werkzeug.wrappers import Response as BaseResponse

from .utils import NS_PREFIX, get_idp_data_dict


def login_discover() -> str:
    """Discovery page for chosing an IdP."""
    return render_template(
        "invenio_edugain/login_discovery.html",
        idp_data_dict=get_idp_data_dict(),
    )


def authn_request() -> BaseResponse:
    """Send an authorization-request to IdP depending on `request.args`.

    request.args["id"] identifies the IdP to send the request to
    request.args["next"] determines where to redirect to after response
    """
    # parse search params for entityid, next
    entityid = request.args.get("id")
    if entityid is None:
        abort(400, description="Missing required parameter: id")
    relay_state = request.args.get("next", "/")  # TODO: make default configurable

    # pysaml2: create authn-request
    config_dict = current_app.config["EDUGAIN_PYSAML2_CONFIG"]
    config = SPConfig()
    config.load(config_dict)
    client = Saml2Client(config)
    request_id, http_args = client.prepare_for_authenticate(
        entityid=entityid,
        relay_state=relay_state,
        nsprefix=NS_PREFIX,
    )

    # create flask redirect from pysaml2
    redirect_urls = [
        header_value
        for header_name, header_value in http_args["headers"]
        if header_name == "Location"
    ]
    if len(redirect_urls) != 1:
        # this shouldn't ever happen...
        msg = "pysaml2 gave multiple redirect urls"
        raise ValueError(msg)
    redirect_url = redirect_urls[0]
    redirect_kwargs = {}
    if http_status_code := http_args.get("status"):
        redirect_kwargs["code"] = http_status_code

    return redirect(redirect_url, **redirect_kwargs)


def create_blueprint(app: Flask) -> Blueprint:
    """Create blueprint for invenio-edugain."""
    routes = app.config["EDUGAIN_ROUTES"]
    blueprint = Blueprint(
        "invenio_edugain",
        __name__,
        static_folder="static",
        template_folder="templates",
        url_prefix="/saml",
    )

    blueprint.add_url_rule(routes["login-discover"], view_func=login_discover)
    blueprint.add_url_rule(routes["authn-request"], view_func=authn_request)

    return blueprint
