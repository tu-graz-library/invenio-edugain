# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""
Static config for our SP.

This is a static configuration for now, until configuration building is implemented.
"""

from saml2 import BINDING_HTTP_POST
from saml2.entity_category.edugain import COC
from saml2.entity_category.refeds import RESEARCH_AND_SCHOLARSHIP
from saml2.saml import NAME_FORMAT_URI
from saml2.sigver import get_xmlsec_binary
from saml2.xmldsig import DIGEST_SHA256, SIG_RSA_SHA256

from invenio_edugain.build_config.pysaml2_core import JSON

sample_flask_config: dict[str, JSON] = {
    "EDUGAIN_GEANT_COC_COMPLIANT": True,
    "EDUGAIN_REFEDS_COMPLIANT": True,
    "EDUGAIN_CONTACT_SECURITY_EMAIL": "repository-support@foo.org",
    "EDUGAIN_CONTACT_SECURITY_GIVEN_NAME": "Security",
    "EDUGAIN_CONTACT_SECURITY_SUR_NAME": "Contact",
    "EDUGAIN_CONTACT_SUPPORT_EMAIL": "repository-support@foo.org",
    "EDUGAIN_CONTACT_SUPPORT_GIVEN_NAME": "Technical",
    "EDUGAIN_CONTACT_SUPPORT_SUR_NAME": "Support",
    "EDUGAIN_ENCRYPTION_CERT": "tests/build_config/pki/encryption.crt",
    "EDUGAIN_ENCRYPTION_KEY": "tests/build_config/pki/encryption.key",
    "EDUGAIN_SIGNING_CERT": "tests/build_config/pki/signing.crt",
    "EDUGAIN_SIGNING_KEY": "tests/build_config/pki/signing.key",
    "EDUGAIN_ORG_DISPLAYNAMES_BY_LANG": {
        "en": "Foo University of Technology",
        "de": "Technische Universität Foo",
    },
    "EDUGAIN_ORG_NAMES_BY_LANG": {
        "en": "Foo University of Technology",
        "de": "Technische Universität Foo",
    },
    "EDUGAIN_ORG_URLS_BY_LANG": {
        "en": "https://www.foo.org/home",
        "de": "https://www.foo.org/de/home",
    },
    "EDUGAIN_MAIN_SERVER_DOMAIN": "https://repository.foo.org",  # main domain invenio service runs under, this also determines the id of the SP
    "EDUGAIN_OTHER_SERVER_DOMAINS": [  # other URLs that run the same SP service (e.g. test/demo servers)
        "https://demo.repository.foo.org",
    ],
    "EDUGAIN_SERVICE_DESCRIPTION_EN": "The Foo Repository is a platform of Foo University of Technology for publishing and storing scientific papers, powered by invenio.",
    "EDUGAIN_SERVICE_NAME_EN": "Foo Repository",
    "EDUGAIN_UIINFO_DESCRIPTIONS_BY_LANG": {
        "en": "The Foo Repository is a platform of Foo University of Technology for publishing and storing scientific papers, powered by invenio.",
        "de": "Das Foo Repository ist eine Plattform der Technischen Universität Foo für das Veröffentlichen und Speichern von wissenschaftlichen Arbeiten, powered by invenio.",
    },
    "EDUGAIN_UIINFO_DISPLAYNAMES_BY_LANG": {
        "en": "Foo Repository",
        "de": "Foo Repository",
    },
    "EDUGAIN_UIINFO_LOGOS": [
        {
            "height": "177",
            "width": "177",
            "text": "https://repository.foo.org/static/images/logo.png",
        },
    ],
    "EDUGAIN_UIINFO_PRIVACY_URLS_BY_LANG": {
        "en": "https://repository.foo.org/static/documents/Foo_Repository_General_Data_Protection_Rights_en.pdf",
        "de": "https://repository.foo.org/static/documents/Foo_Repository_General_Data_Protection_Rights_de.pdf",
    },
    "EDUGAIN_UIINFO_INFO_URLS_BY_LANG": {
        "en": "https://repository.foo.org/",
        "de": "https://repository.foo.org/",
    },
}


sp_config_dict = {
    "allow_unsolicited": True,
    "authn_requests_signed": False,
    "digest_algorithm": DIGEST_SHA256,
    "endpoints": {
        "assertion_consumer_service": [
            # NOTE: usually, these would be EDUGAIN_MAIN_SERVER_DOMAIN followed by EDUGAIN_OTHER_SERVER_DOMAINS
            # however, test-function adds the localhost line
            ("https://repository.foo.org/saml/acs", BINDING_HTTP_POST),
            ("https://localhost:5000/saml/acs", BINDING_HTTP_POST),
            ("https://demo.repository.foo.org/saml/acs", BINDING_HTTP_POST),
        ],
    },
    "force_authn": False,
    "name_id_format_allow_create": True,  # NOTE: this only shows in <AuthnRequest> when "requested_attributes" is truthy
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
    "ui_info": {
        "description": [
            {
                "text": "The Foo Repository is a platform of Foo University of Technology for publishing and storing scientific papers, powered by invenio.",
                "lang": "en",
            },
            {
                "text": "Das Foo Repository ist eine Plattform der Technischen Universität Foo für das Veröffentlichen und Speichern von wissenschaftlichen Arbeiten, powered by invenio.",
                "lang": "de",
            },
        ],
        "display_name": [
            {"text": "Foo Repository", "lang": "en"},
            {"text": "Foo Repository", "lang": "de"},
        ],
        "information_url": [
            {"text": "https://repository.foo.org/", "lang": "en"},
            {"text": "https://repository.foo.org/", "lang": "de"},
        ],
        "logo": [
            {
                "height": "177",
                "width": "177",
                "text": "https://repository.foo.org/static/images/logo.png",
            },
        ],
        "privacy_statement_url": [
            {
                "text": "https://repository.foo.org/static/documents/Foo_Repository_General_Data_Protection_Rights_en.pdf",
                "lang": "en",
            },
            {
                "text": "https://repository.foo.org/static/documents/Foo_Repository_General_Data_Protection_Rights_de.pdf",
                "lang": "de",
            },
        ],
    },
    "want_assertions_signed": False,
    "want_assertions_or_response_signed": True,
    "want_response_signed": False,
}


expected_sample_config = {
    "accepted_time_diff": 60,  # IdPs' clock may drift from our server's clock by this many seconds
    "allow_unknown_attributes": True,  # IdPs can send wildly different attributes, allow all of them to appear in parsed output
    "contact_person": [
        {
            "email_address": ["mailto:repository-support@foo.org"],
            "given_name": "Technical",
            "sur_name": "Support",
            "contact_type": "technical",
        },
        {
            "email_address": ["mailto:repository-support@foo.org"],
            "extension_attributes": {
                "xmlns:remd": "http://refeds.org/metadata",
                "remd:contactType": "http://refeds.org/metadata/contactType/security",
            },
            "given_name": "Security",
            "sur_name": "Contact",
            "contact_type": "other",
        },
    ],
    "description": (  # NOTE: due to internal config-representation in pysaml2, only one description can be given
        "The Foo Repository is a platform of Foo University of Technology for publishing and storing scientific papers, powered by invenio.",
        "en",
    ),
    "entityid": "https://repository.foo.org/saml/sp/xml",  # used for <Issuer> element
    "entity_attributes": [
        {
            "format": NAME_FORMAT_URI,
            "name": "urn:oasis:names:tc:SAML:profiles:subject-id:req",
            "values": ["any"],
        },
    ],
    "entity_category": [COC, RESEARCH_AND_SCHOLARSHIP],
    "http_client_timeout": 10,
    "metadata": [
        {
            "class": "invenio_edugain.utils.MetaDataFlaskSQL",
            "metadata": [(None,)],
        },
    ],
    # NOTE: str() of name is used as ProviderName in AuthnRequests, so don't use (lang, text) tuple here;
    #       this is hence interpreted as default-language "en"
    #       (due to internal config-representation in pysaml2, only one language would be givable anyway)
    "name": "Foo Repository",
    "logging": None,
    "organization": {
        "name": [
            ("Foo University of Technology", "en"),
            ("Technische Universität Foo", "de"),
        ],
        "display_name": [
            ("Foo University of Technology", "en"),
            ("Technische Universität Foo", "de"),
        ],
        "url": [
            ("https://www.foo.org/home", "en"),
            ("https://www.foo.org/de/home", "de"),
        ],
    },
    "service": {
        "sp": sp_config_dict,
    },
    "key_file": "tests/build_config/pki/signing.key",
    "cert_file": "tests/build_config/pki/signing.crt",
    "encryption_keypairs": [
        # security best practice is to never use the same key for two things
        # (probably doesn't really matter in this case in particular though)
        {
            "key_file": "tests/build_config/pki/encryption.key",
            "cert_file": "tests/build_config/pki/encryption.crt",
        },
    ],
    "xmlsec_binary": get_xmlsec_binary(["/opt/local/bin", "/usr/local/bin"]),
}
