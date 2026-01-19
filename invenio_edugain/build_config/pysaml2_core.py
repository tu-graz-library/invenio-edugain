# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Core config classes for later expansion into pysaml2 config dict."""

import json
from collections.abc import Mapping
from dataclasses import Field, InitVar, dataclass, field, fields
from typing import Any, get_origin

from .utils import (
    ABSENT,
    JSON,
    EdugainConfigCoreExceptionGroup,
    Email,
    FilePath,
    LangDict,
    LogoList,
    ValueExceptionTuple,
    field_for,
)


@dataclass
class Pysaml2ConfigCoreBase:
    """Base class for `Pysaml2ConfigCore...` classes.

    The `Core` in the name signals that this isn't the full configuration,
    but rather the minimally necessary *core* part of the configuration.
    This class provides validation, type-coercion, and loading of missing fields from a flask app config.
    """

    flask_config: InitVar[Mapping[str, JSON] | None] = field(
        default=None,
        kw_only=True,
    )

    @staticmethod
    def get_field_type(field: Field) -> type:
        """Get a field's type.

        There's some quirks to getting type due to annotations like `: dict[str, str]` and `: "int"` (mind the `"`).
        """
        # this gets original type of or generic type, e.g. get_origin(dict[str, str]) is dict
        field_type = get_origin(field.type) or field.type
        # prevent type-annotations like `v: "int"` (mind the `"`)
        assert isinstance(field_type, type)

        return field_type

    def coerce_type(
        self,
        field: Field,
        field_value: Any,  # noqa: ANN401
    ) -> ValueExceptionTuple:
        """Attemp to coerce `field_value` to `field`'s type."""
        field_type = self.get_field_type(field)
        try:
            field_value = field_type(field_value)
        except Exception as exc:  # noqa: BLE001
            exc.add_note(
                f"when coercing value for field `{field.name}` to `{field_type.__module__}.{field_type.__qualname__}`, value was {field_value!r}",
            )
            return ValueExceptionTuple(exception=exc)

        return ValueExceptionTuple(value=field_value)

    def get_field_value_from_flask_config(
        self,
        field: Field,
        flask_config: Mapping[str, JSON] | None,
    ) -> ValueExceptionTuple:
        """Get value for `field` from `flask_config`.

        `field` must have configured field.metadata["flask_config_key"] for this to work.
        """
        field_type = self.get_field_type(field)

        # fields without configured `flask_config_key` cannot be gotten from flask and must be passed instead
        if "flask_config_key" not in field.metadata:
            msg = f"`{field.name}`: must pass a value for this field"
            return ValueExceptionTuple(exception=TypeError(msg))
        flask_config_key = field.metadata["flask_config_key"]

        if flask_config is None:
            msg = f'`{field.name}`: must pass either `{field.name}` or `flask_config` with "{flask_config_key}" set'
            return ValueExceptionTuple(exception=TypeError(msg))

        if flask_config_key not in flask_config:
            msg = (
                f'`{field.name}`: no "{flask_config_key}" in given `flask_config`\n'
                f'either add "{flask_config_key}" to `flask_config`, or pass `{field.name}`'
            )
            return ValueExceptionTuple(exception=KeyError(msg))
        field_value = flask_config[flask_config_key]

        # config-var might come from env-var, in which case it's of type str
        # attempt JSON-parsing such values when target-type is dict/list
        if isinstance(field_value, str) and (issubclass(field_type, (list, dict))):
            try:
                field_value = json.loads(field_value)
            except Exception as exc:  # noqa: BLE001
                exc.add_note(
                    f'when JSON-parsing value for "{flask_config_key}", value was {field_value!r}',
                )
                return ValueExceptionTuple(exception=exc)

        field_value, exception = self.coerce_type(field, field_value)
        if exception:
            return ValueExceptionTuple(exception=exception)

        return ValueExceptionTuple(value=field_value)

    def parse_fields(self, flask_config: Mapping[str, JSON] | None) -> list[Exception]:
        """Attempt filling in ABSENT fields from `flask_config`, do some checks."""
        exceptions: list[Exception] = []
        for field in fields(self):  # noqa: F402  # shadows imported dataclasses.field
            field_type = self.get_field_type(field)
            field_value = getattr(self, field.name)

            if field_value is ABSENT and issubclass(field_type, Pysaml2ConfigCoreBase):
                try:
                    field_value = field_type(flask_config=flask_config)
                except EdugainConfigCoreExceptionGroup as exception_group:
                    exception_group = exception_group.with_traceback(None)
                    exception_group.add_note(
                        f"when automatically building from `flask_config` as its parent wasn't exlicitly passed `{field.name}`",
                    )
                    exceptions.append(exception_group)
                    continue

            elif field_value is ABSENT:  # but isn't a Pysaml2ConfigCore class
                field_value, exception = self.get_field_value_from_flask_config(
                    field,
                    flask_config,
                )
                if exception:
                    exceptions.append(exception)
                    continue

            else:  # field_value is not ABSENT
                field_value, exception = self.coerce_type(field, field_value)
                if exception:
                    exceptions.append(exception)
                    continue

            setattr(self, field.name, field_value)

        return exceptions

    def __post_init__(self, flask_config: Mapping[str, JSON] | None) -> None:
        """Read ABSENT fields from `flask_config`, coerce types, run some checks."""
        exceptions = self.parse_fields(flask_config=flask_config)
        if exceptions:
            msg = f"error when initializing {type(self).__module__}.{type(self).__qualname__}"
            raise EdugainConfigCoreExceptionGroup(msg, exceptions)


@dataclass
class Pysaml2ConfigCoreContacts(Pysaml2ConfigCoreBase):
    """Holds info on contacts to be contacted when issues arise, used for creating a pysaml2 config.

    Unprovided fields are taken from provided `flask_config`.
    Emails may be provided as strings, they will be parsed into `Email`s automatically.
    """

    security_contact_email: Email = field_for(  # noqa: RUF009
        "EDUGAIN_CONTACT_SECURITY_EMAIL",
    )
    security_contact_given_name: str = field_for("EDUGAIN_CONTACT_SECURITY_GIVEN_NAME")
    security_contact_sur_name: str = field_for("EDUGAIN_CONTACT_SECURITY_SUR_NAME")
    technical_support_email: Email = field_for(  # noqa: RUF009
        "EDUGAIN_CONTACT_SUPPORT_EMAIL",
    )
    technical_support_given_name: str = field_for("EDUGAIN_CONTACT_SUPPORT_GIVEN_NAME")
    technical_support_sur_name: str = field_for("EDUGAIN_CONTACT_SUPPORT_SUR_NAME")


@dataclass
class Pysaml2ConfigCoreCryptographicCredentials(Pysaml2ConfigCoreBase):
    """Holds cryptograhic credential related fields, used for creating a pysaml2 config.

    Unprovided fields are taken from provided `flask_config`.
    """

    encryption_cert_filepath: FilePath = field_for(  # noqa: RUF009
        "EDUGAIN_ENCRYPTION_CERT",
    )
    encryption_key_filepath: FilePath = field_for(  # noqa: RUF009
        "EDUGAIN_ENCRYPTION_KEY",
    )
    signing_cert_filepath: FilePath = field_for("EDUGAIN_SIGNING_CERT")  # noqa: RUF009
    signing_key_filepath: FilePath = field_for("EDUGAIN_SIGNING_KEY")  # noqa: RUF009


@dataclass
class Pysaml2ConfigCoreEntityCategories(Pysaml2ConfigCoreBase):
    """Holds entity-categories information, used for creating a pysaml2 config.

    Unprovided fields are taken from provided `flask_config`.
    """

    # claims compliance with Geant CoC
    geant_coc_compliant: bool = field_for("EDUGAIN_GEANT_COC_COMPLIANT")
    # claims compliance with REFEDS research and scholarship
    refeds_compliant: bool = field_for("EDUGAIN_REFEDS_COMPLIANT")


@dataclass
class Pysaml2ConfigCoreOrganization(Pysaml2ConfigCoreBase):
    """Holds info related to the organization running the SP, used for creating a pysaml2 config.

    Unprovided fields are taken from provided `flask_config`.
    """

    displaynames_by_lang: LangDict = field_for(  # noqa: RUF009
        "EDUGAIN_ORG_DISPLAYNAMES_BY_LANG",
    )
    names_by_lang: LangDict = field_for("EDUGAIN_ORG_NAMES_BY_LANG")  # noqa: RUF009
    urls_by_lang: LangDict = field_for("EDUGAIN_ORG_URLS_BY_LANG")  # noqa: RUF009


@dataclass
class Pysaml2ConfigCoreProvidedService(Pysaml2ConfigCoreBase):
    """Holds info on the provided service, used for creating a pysaml2 config.

    Unprovided fields are taken from provided `flask_config`.
    """

    # NOTE: due to internal representation used by pysaml2, only "en"glish names are givable here
    description_en: str = field_for("EDUGAIN_SERVICE_DESCRIPTION_EN")
    name_en: str = field_for("EDUGAIN_SERVICE_NAME_EN")


@dataclass
class Pysaml2ConfigCoreUIInfo(Pysaml2ConfigCoreBase):
    """Holds info shown to users about this SP, used for creating a pysaml2 config.

    Unprovided fields are taken from provided `flask_config`.
    """

    descriptions_by_lang: LangDict = field_for(  # noqa: RUF009
        "EDUGAIN_UIINFO_DESCRIPTIONS_BY_LANG",
    )
    displaynames_by_lang: LangDict = field_for(  # noqa: RUF009
        "EDUGAIN_UIINFO_DISPLAYNAMES_BY_LANG",
    )
    information_urls_by_lang: LangDict = field_for(  # noqa: RUF009
        "EDUGAIN_UIINFO_INFO_URLS_BY_LANG",
    )
    logos: LogoList = field_for(  # noqa: RUF009
        "EDUGAIN_UIINFO_LOGOS",
    )
    privacy_statement_urls_by_lang: LangDict = field_for(  # noqa: RUF009
        "EDUGAIN_UIINFO_PRIVACY_URLS_BY_LANG",
    )


@dataclass
class Pysaml2ConfigCore(Pysaml2ConfigCoreBase):
    """Holds core pysaml2 config fields that MUST be user-provided.

    Fields may be passed directly, automatically generated from a passed `flask_config`, or any combination therof.

    e.g. organization-name MUST be provided (as we cannot possibly know it), but timeout can be left at default
    Is used to create a full pysaml2 config from this core.
    """

    category: Pysaml2ConfigCoreEntityCategories = field(default=ABSENT)  # type: ignore[assignment]
    contact: Pysaml2ConfigCoreContacts = field(default=ABSENT)  # type: ignore[assignment]
    credentials: Pysaml2ConfigCoreCryptographicCredentials = field(default=ABSENT)  # type: ignore[assignment]
    org: Pysaml2ConfigCoreOrganization = field(default=ABSENT)  # type: ignore[assignment]
    server_domain_main: str = field_for("EDUGAIN_MAIN_SERVER_DOMAIN")
    server_domain_others: list[str] = field_for(  # noqa: RUF009
        "EDUGAIN_OTHER_SERVER_DOMAINS",
    )
    service: Pysaml2ConfigCoreProvidedService = field(default=ABSENT)  # type: ignore[assignment]
    ui_info: Pysaml2ConfigCoreUIInfo = field(default=ABSENT)  # type: ignore[assignment]
