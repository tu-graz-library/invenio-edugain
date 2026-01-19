# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Build configuration for pysaml2."""
from flask import Flask
from saml2 import BINDING_HTTP_POST
from saml2.entity_category.edugain import COC
from saml2.entity_category.refeds import RESEARCH_AND_SCHOLARSHIP
from saml2.saml import NAME_FORMAT_URI
from saml2.sigver import get_xmlsec_binary
from saml2.xmldsig import DIGEST_SHA256, SIG_RSA_SHA256

from .pysaml2_core import Pysaml2ConfigCore
from .utils import url_for_server

type JSONplusTuples = (
    str
    | int
    | float
    | bool
    | None
    | dict[str, JSONplusTuples]
    | list[JSONplusTuples]
    | tuple[JSONplusTuples, ...]  # unlike JSON, this also contains tuples
)
"""JSON extended by tuples, for typing pysaml2 config (which includes tuples).

The inclusion of tuples was considered different enough to introduce this new type."""


def build_pysaml2_config(
    app: Flask,
    config_core: Pysaml2ConfigCore,
) -> dict[str, JSONplusTuples]:
    """Build configuration for use with pysaml2."""
    # contacts
    contacts: list[JSONplusTuples] = [
        {
            "email_address": [
                f"mailto:{config_core.contact.technical_support_email.normalized}",
            ],
            "given_name": config_core.contact.technical_support_given_name,
            "sur_name": config_core.contact.technical_support_sur_name,
            "contact_type": "technical",
        },
        {
            "email_address": [
                f"mailto:{config_core.contact.security_contact_email.normalized}",
            ],
            "extension_attributes": {
                "xmlns:remd": "http://refeds.org/metadata",
                "remd:contactType": "http://refeds.org/metadata/contactType/security",
            },
            "given_name": config_core.contact.security_contact_given_name,
            "sur_name": config_core.contact.security_contact_sur_name,
            "contact_type": "other",
        },
    ]

    # entity_categories
    entity_categories = []
    if config_core.category.geant_coc_compliant:
        entity_categories.append(COC)
    if config_core.category.refeds_compliant:
        entity_categories.append(RESEARCH_AND_SCHOLARSHIP)

    # organization
    organization: dict[str, JSONplusTuples] = {}
    organization["name"] = [
        (name, lang_code) for lang_code, name in config_core.org.names_by_lang.items()
    ]
    organization["display_name"] = [
        (display_name, lang_code)
        for lang_code, display_name in config_core.org.displaynames_by_lang.items()
    ]
    organization["url"] = [
        (url, lang_code) for lang_code, url in config_core.org.urls_by_lang.items()
    ]

    return {
        "accepted_time_diff": 60,  # IdPs' clock may drift from our server's clock by this many seconds
        "allow_unknown_attributes": True,  # IdPs can send wildly different attributes, allow all of them to appear in parsed output
        "contact_person": contacts,
        "description": (
            config_core.service.description_en,
            "en",
        ),  # NOTE: due internal config-representation in pysaml2, only one description can be given
        "entityid": url_for_server(
            app,
            config_core.server_domain_main,
            "invenio_edugain.sp_xml",
        ),
        "entity_attributes": [
            {
                "format": NAME_FORMAT_URI,
                "name": "urn:oasis:names:tc:SAML:profiles:subject-id:req",
                "values": ["any"],
            },
        ],
        "entity_category": entity_categories,
        "http_client_timeout": 10,
        "logging": None,
        "metadata": [  # configure metadata-loader that loads from SQL
            {
                "class": "invenio_edugain.utils.MetaDataFlaskSQL",
                "metadata": [(None,)],
            },
        ],
        # NOTE: str() of name is used as ProviderName in AuthnRequests, so don't use (lang, text) tuple here;
        #       this is hence interpreted as default-language "en"
        #       (due to internal config-representation in pysaml2, only one language would be givable anyway)
        "name": config_core.service.name_en,
        "organization": organization,
        "service": {
            "sp": build_sp(app, config_core),
        },
        "cert_file": str(config_core.credentials.signing_cert_filepath),
        "key_file": str(config_core.credentials.signing_key_filepath),
        "encryption_keypairs": [
            {
                "key_file": str(config_core.credentials.encryption_key_filepath),
                "cert_file": str(config_core.credentials.encryption_cert_filepath),
            },
        ],
        "xmlsec_binary": get_xmlsec_binary(["/opt/local/bin", "/usr/local/bin"]),
    }


def build_sp(app: Flask, core_config: Pysaml2ConfigCore) -> dict[str, JSONplusTuples]:
    """Build 'sp' part of a pysaml2 configuration."""
    # acs_enpoints
    acs_endpoints: list[JSONplusTuples] = [
        (url_for_server(app, domain, "invenio_edugain.acs"), BINDING_HTTP_POST)
        for domain in [
            core_config.server_domain_main,
            *core_config.server_domain_others,
        ]
    ]

    # ui-info
    ui_info: dict[str, JSONplusTuples] = {}
    ui_info["description"] = [
        {"text": text, "lang": lang_code}
        for lang_code, text in core_config.ui_info.descriptions_by_lang.items()
    ]
    ui_info["display_name"] = [
        {"text": text, "lang": lang_code}
        for lang_code, text in core_config.ui_info.displaynames_by_lang.items()
    ]
    ui_info["information_url"] = [
        {"text": text, "lang": lang_code}
        for lang_code, text in core_config.ui_info.information_urls_by_lang.items()
    ]
    ui_info["privacy_statement_url"] = [
        {"text": text, "lang": lang_code}
        for lang_code, text in core_config.ui_info.privacy_statement_urls_by_lang.items()
    ]

    ui_info["logo"] = list(core_config.ui_info.logos)  # type: ignore[arg-type]  # type is correct as it is checked at initialization of .logos, but mypy can't tell

    return {
        "allow_unsolicited": True,
        "authn_requests_signed": False,
        "digest_algorithm": DIGEST_SHA256,
        "endpoints": {
            "assertion_consumer_service": acs_endpoints,
        },
        "force_authn": False,
        "name_id_format_allow_create": True,
        "optional_attributes": [
            "eduPersonPrincipalName",
            "eduPersonScopedAffiliation",
        ],
        "signing_algorithm": SIG_RSA_SHA256,
        "requested_attributes": [],
        "required_attributes": [
            "displayName",
            "givenName",
            "mail",
            "sn",
        ],
        "ui_info": ui_info,
        "want_assertions_signed": False,
        "want_assertions_or_response_signed": True,
        "want_response_signed": False,
    }
