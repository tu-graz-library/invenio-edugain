# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""invenio-edugain views."""

from xml.etree import ElementTree as ET

from flask import (
    Blueprint,
    Flask,
    Response,
    abort,
    current_app,
    redirect,
    render_template,
    request,
)
from flask_security import login_user
from saml2.client import Saml2Client
from saml2.config import Config, SPConfig
from saml2.metadata import entity_descriptor
from werkzeug.wrappers import Response as BaseResponse

from .utils import (
    NS_PREFIX,
    AuthnInfo,
    AuthnResponseError,
    create_user,
    get_idp_data_dict,
)


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
    _request_id, http_args = client.prepare_for_authenticate(
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


def sp_xml() -> Response:
    """Show SAML xml-metadata of this service provider."""
    config_dict = current_app.config["EDUGAIN_PYSAML2_CONFIG"]
    config = Config()
    config.load(config_dict)
    ed = entity_descriptor(config)

    # clean up xml-representation
    ed_etree = ET.XML(ed.to_string(NS_PREFIX))
    ET.indent(ed_etree)
    xml_bytes = ET.tostring(ed_etree, xml_declaration=True)

    return Response(xml_bytes, mimetype="application/xml")


def acs() -> BaseResponse:
    """Assertion consumer service."""  # noqa:D401
    next_url = request.form.get("RelayState")
    saml_response = request.form.get("SAMLResponse")
    if saml_response is None:
        msg = "POST contained no SAMLResponse"
        raise AuthnResponseError(msg)

    authn_info = AuthnInfo.from_saml_response(saml_response)
    if authn_info.user is None:
        # no user found in db, create one
        authn_info.user = create_user(authn_info)

    if not login_user(authn_info.user):
        # user.active is False, hence wasn't logged in
        msg = "User was blocked/deactivated"
        raise AuthnResponseError(msg)
    current_app.extensions["security"].datastore.commit()

    return redirect(next_url or current_app.config["SECURITY_POST_LOGIN_VIEW"])


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

    blueprint.add_url_rule(routes["acs"], methods=["POST"], view_func=acs)
    blueprint.add_url_rule(routes["authn-request"], view_func=authn_request)
    blueprint.add_url_rule(routes["sp-xml"], view_func=sp_xml)

    return blueprint
