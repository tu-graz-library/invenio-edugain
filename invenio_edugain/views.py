# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""invenio-edugain views."""

from collections import defaultdict
from secrets import token_hex
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
from invenio_db import db
from invenio_i18n.proxies import current_i18n
from invenio_oauthclient.utils import get_safe_redirect_target
from saml2.client import Saml2Client
from saml2.config import Config, SPConfig
from saml2.mdstore import MetadataStore
from saml2.metadata import entity_descriptor
from werkzeug.wrappers import Response as BaseResponse

from .models import IdPData
from .utils import (
    NS_PREFIX,
    AuthnInfo,
    AuthnResponseError,
    create_user,
    secure_redirect_url,
)


def login_discover() -> str:
    """Discovery page for choosing an IdP."""
    shibboleth_eds_config = current_app.config["EDUGAIN_SHIBBOLETH_EDS_CONFIG"]
    shibboleth_eds_config["selectedLanguage"] = current_i18n.language

    return render_template(
        "invenio_edugain/login_discovery.html",
        shibboleth_eds_config=shibboleth_eds_config,
    )


def disco_feed() -> list:
    """Return disco feed for use with shibboleth EDS."""
    config_dict = current_app.config["EDUGAIN_PYSAML2_CONFIG"]
    config = Config()
    config.load(config_dict)
    mds: MetadataStore = config.metadata

    discoverable_query = db.select(
        IdPData.id,
    ).where(
        IdPData.discoverable == db.true(),
        IdPData.enabled == db.true(),
    )
    discoverable_idp_ids: set[str] = set(db.session.scalars(discoverable_query))

    feed = []
    available_idp_ids = sorted(set(mds.identity_providers()) & discoverable_idp_ids)
    for idp_id in available_idp_ids:
        # entry is one item in the feed
        entry: dict[str, list | str] = {"entityID": idp_id}

        names_by_lang = defaultdict(list)  # names ordered by relevance
        uiinfos = list(mds.mdui_uiinfo(idp_id))
        for uiinfo in uiinfos:
            for dn in uiinfo.get("display_name", []):
                names_by_lang[dn["lang"]].append(dn["text"])
        org = mds[idp_id].get("organization", {})
        for name_key in [
            "organization_display_name",
            "organization_name",
            "organization_url",
        ]:
            for name_dict in org.get(name_key, []):
                names_by_lang[name_dict["lang"]].append(name_dict["text"])

        entry["DisplayNames"] = [
            {"lang": lang, "value": names[0]} for lang, names in names_by_lang.items()
        ]

        entry["Keywords"] = [
            {"lang": kw["lang"], "value": kw["text"]}
            for uiinfo in uiinfos
            for kw in uiinfo.get("keywords", [])
        ]

        logo_entries = []
        for uiinfo in uiinfos:
            for logo in uiinfo.get("logo", []):
                logo_entry = {
                    "value": logo["text"],
                    "height": logo["height"],
                    "width": logo["width"],
                }
                if "lang" in logo:
                    logo_entry["lang"] = logo["lang"]
                logo_entries.append(logo_entry)
        entry["Logos"] = logo_entries

        feed.append(entry)

    return feed


def authn_request() -> BaseResponse:
    """Send an authorization-request to IdP depending on `request.args`.

    request.args["id"] identifies the IdP to send the request to
    request.args["next"] determines where to redirect to after response
    """
    # parse search params for entityid, next
    entityid = request.args.get("entityID")
    if entityid is None:
        abort(400, description="Missing required parameter: id")

    # "relay state" is SAML's name for "URL to redirect to after succesful login"
    relay_state: str = (
        get_safe_redirect_target(arg="next")
        or current_app.config.get("SECURITY_POST_LOGIN_VIEW")
        or "/"
    )

    # pysaml2: create authn-request
    config_dict = current_app.config["EDUGAIN_PYSAML2_CONFIG"]
    config = SPConfig()
    config.load(config_dict)
    client = Saml2Client(config)

    # multiple ACS URLs may be configured for `client` (e.g. test-, prod-server)
    # find the ACS URL corresponding to the request's host
    host_url = request.host_url
    assertion_consumer_service_url = None
    for url in client.service_urls():
        if url.startswith(host_url):
            assertion_consumer_service_url = url
            break
    else:
        abort(400, description="No ACS configured for this host")

    _request_id, http_args = client.prepare_for_authenticate(
        entityid=entityid,
        relay_state=relay_state,
        nsprefix=NS_PREFIX,
        assertion_consumer_service_url=assertion_consumer_service_url,
    )

    # create flask redirect from pysaml2
    redirect_urls = [
        header_value
        for header_name, header_value in http_args["headers"]
        if header_name == "Location"
    ]
    if len(redirect_urls) < 1:
        # this shouldn't ever happen...
        msg = "pysaml2 gave no redirect urls"
        raise ValueError(msg)
    if len(redirect_urls) > 1:
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
    xml_bytes = ET.tostring(ed_etree, xml_declaration=True, encoding="utf-8")

    return Response(
        xml_bytes,
        content_type="application/xml; charset=utf-8",
        mimetype="application/xml",
    )


def acs() -> BaseResponse:
    """Assertion consumer service."""  # noqa:D401
    next_url = secure_redirect_url(request.form.get("RelayState", ""))
    saml_response = request.form.get("SAMLResponse")
    if saml_response is None:
        msg = "POST contained no SAMLResponse"
        raise AuthnResponseError(msg)

    authn_info = AuthnInfo.from_saml_response(saml_response)
    if authn_info.user is None:
        # no user found in db, create one
        # to prevent name collisions of users with same name, use random username instead
        # we never show username to other users anyway...
        # 16 bytes means chance of collisions is virtually 0 up to about 10**15 users
        authn_info.suggested_username = "user-" + token_hex(nbytes=16)
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

    # note that app-entrypoints are loaded before blueprint-entrypoints, so this exists
    talisman = app.extensions.get("invenio-app", None).talisman
    default_csp = talisman.content_security_policy

    # this is a decorator for views that sets their Content-Security-Policy
    allow_imgsrc_csp = talisman(
        content_security_policy=default_csp | {"img-src": "*"},
    )
    # apply decorator (note that @decorator syntax is just syntactic sugar for calling the func)
    match app.config.get("EDUGAIN_ALLOW_IMGSRC_CSP"):
        case True:
            discover_view = allow_imgsrc_csp(login_discover)
        case False:
            discover_view = login_discover
        case _:
            msg = (
                "Please decide whether you allow 'imgsrc: *' Content-Security-Policy for discovery page, "
                "then set EDUGAIN_ALLOW_IMGSRC_CSP accordingly"
            )
            raise ValueError(msg)

    blueprint.add_url_rule(routes["acs"], methods=["POST"], view_func=acs)
    blueprint.add_url_rule(routes["authn-request"], view_func=authn_request)
    blueprint.add_url_rule(routes["discofeed"], view_func=disco_feed)
    blueprint.add_url_rule(routes["login-discover"], view_func=discover_view)
    blueprint.add_url_rule(routes["sp-xml"], view_func=sp_xml)

    return blueprint
