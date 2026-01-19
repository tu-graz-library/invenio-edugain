# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utils for building configs."""

import enum
from collections.abc import Callable
from dataclasses import field
from pathlib import Path
from typing import Any, Literal, NamedTuple

from email_validator import ValidatedEmail, validate_email
from flask import Flask
from flask.app import BuildError
from uritools import uricompose, urisplit


class _ABSENT(enum.Enum):
    """Sentinel distinguishable from `None`."""

    ABSENT = enum.auto()

    def __repr__(self) -> str:
        return "ABSENT"

    def __bool__(self) -> Literal[False]:
        return False


ABSENT = _ABSENT.ABSENT
type AbsentType = Literal[_ABSENT.ABSENT]

type JSON = str | int | float | bool | None | dict[str, JSON] | list[JSON]


class EdugainConfigCoreExceptionGroup(ExceptionGroup):
    """Exception group used by `Pysaml2ConfigCore...` classes, distinguishable from `ExceptionGroup`."""


class ValueExceptionTuple(NamedTuple):
    """Holds result and exceptions."""

    value: Any = None
    exception: Exception | None = None


class Email(ValidatedEmail):
    """A subclass of ValidatedEmail that can be initialized with a str."""

    def __init__(self, email_address: str | ValidatedEmail) -> None:
        """Init."""
        if isinstance(email_address, ValidatedEmail):
            self._validated_email = email_address
        else:
            self._validated_email = validate_email(
                email_address,
                check_deliverability=False,
            )

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        """Getattr."""
        return getattr(self._validated_email, name)


class LangDict(dict[str, str]):
    """A dict that checks at initialization whether its keys are lang-codes and its values are strings."""

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Init."""
        super().__init__(*args, **kwargs)
        exceptions: list[Exception] = []

        if bad_keys := [k for k in self if not isinstance(k, str)]:
            msg = f"LangDict keys must be str, but these {len(bad_keys)} key(s) weren't: {bad_keys!r}"
            exceptions.append(TypeError(msg))

        if bad_values := [v for v in self.values() if not isinstance(v, str)]:
            msg = f"LangDict values must be str, but these {len(bad_values)} key(s) weren't: {bad_values!r}"
            exceptions.append(TypeError(msg))

        if exceptions:
            msg = f"error when initializing {type(self).__module__}.{type(self).__qualname__}"
            raise ExceptionGroup(msg, exceptions)


class LogoList(list[dict[str, str]]):
    """A list that checks at initialization whether its items are logo-dicts."""

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Init."""
        super().__init__(*args, **kwargs)
        exceptions: list[Exception] = []

        required_keys = {"text", "height", "width"}
        optional_keys = {"lang"}
        for idx, logo_dict in enumerate(self):
            if not isinstance(logo_dict, dict):
                msg = f"LogoList[{idx}] must be dict, but was {type(logo_dict)!r}"
                exceptions.append(TypeError(msg))
                continue

            if bad_values := [v for v in logo_dict.values() if not isinstance(v, str)]:
                msg = f"LogoList[{idx}] values must be str, but these {len(bad_values)} key(s) weren't: {bad_values!r}"
                exceptions.append(TypeError(msg))

            if bad_keys := [k for k in logo_dict if not isinstance(k, str)]:
                msg = f"LogoList[{idx}] keys must be str, but these {len(bad_keys)} key(s) weren't: {bad_keys!r}"
                exceptions.append(TypeError(msg))
                continue

            logo_keys = set(logo_dict)

            if extra_keys := (logo_keys - required_keys) - optional_keys:
                msg = f"LogoList[{idx}] had extraneous key(s): {sorted(extra_keys)}"
                exceptions.append(TypeError(msg))

            if missing_keys := required_keys - logo_keys:
                msg = f"Logolist[{idx}] is missing required key(s): {sorted(missing_keys)}"
                exceptions.append(KeyError(msg))

        if exceptions:
            msg = f"error when initializing {type(self).__module__}.{type(self).__qualname__}"
            raise ExceptionGroup(msg, exceptions)


class FilePath(Path):
    """A path that checks for file-existence at initialization."""

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Init."""
        super().__init__(*args, **kwargs)
        if not self.is_file():
            msg = f"no file at this path: {self.absolute().as_posix()!r}"
            raise FileNotFoundError(msg)


def typing_deco[**P, R](func: Callable[P, R]):  # noqa: ANN201
    """Catch ParamSpec of passed-in func as to apply it to returned `field_for`.

    This only exists s.t. `field_for` can retain type-information.
    """

    def field_for(flask_config_key: str, *args: P.args, **kwargs: P.kwargs) -> R:
        """Construct a field that has a corresponding flask-app config-var."""
        if not kwargs.get("metadata"):
            kwargs["metadata"] = {}
        if not kwargs.get("default"):
            kwargs["default"] = ABSENT
        kwargs["metadata"]["flask_config_key"] = flask_config_key  # type: ignore[index]
        return func(*args, **kwargs)

    return field_for


field_for = typing_deco(field)


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
    elif (split_server_name := urisplit(server_name)).getscheme():
        scheme = split_server_name.getscheme()
        server_name_without_scheme = uricompose(
            scheme=None,
            authority=split_server_name.getauthority(),
            path=split_server_name.getpath(),
            query=split_server_name.getquery(),
            fragment=split_server_name.getfragment(),
        )
        if split_server_name.getauthority():
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
