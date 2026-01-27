# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2026 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test building of pysaml2 config."""

from flask import Flask

from invenio_edugain.build_config import Pysaml2ConfigCore, build_pysaml2_config
from invenio_edugain.build_config.pysaml2 import JSONplusTuples

from .saml_config import expected_sample_config, sample_flask_config


def pprint_path(path: tuple) -> str:
    """PP."""
    return ".".join(str(i) for i in path)


def find_json_mismatches(  # noqa: C901, PLR0912
    generated: JSONplusTuples,
    expected: JSONplusTuples,
    path: tuple = (),
) -> Exception | None:
    """Return exception denoting places in which passed-in JSONs mismatch."""
    if type(expected) is not type(generated):
        return TypeError(
            f"{pprint_path(path)}\ntype-mismatch: expected {type(expected)!r}, generated {type(generated)}",
        )

    errors: list[Exception] = []
    if isinstance(expected, dict) and isinstance(generated, dict):
        # handle JSON types that are mappings
        extra_keys = sorted(set(expected) - set(generated))
        missing_keys = sorted(set(generated) - set(expected))
        common_keys = sorted(set(expected) & set(generated))
        if extra_keys:
            errors.append(KeyError(f"extra-keys {extra_keys}"))
        if missing_keys:
            errors.append(KeyError(f"missing-keys {missing_keys}"))
        for key in common_keys:
            sub_error = find_json_mismatches(
                generated[key],
                expected[key],
                (*path, key),
            )
            if sub_error:
                errors.append(sub_error)
        if errors:
            return ExceptionGroup(pprint_path(path), errors)
    elif isinstance(generated, (list, tuple)) and isinstance(expected, (list, tuple)):
        # handle JSON types that are sequences
        if len(expected) != len(generated):
            errors.append(
                IndexError(
                    f"{pprint_path(path)}: len-differs: expected {len(expected)}, generated {len(generated)}",
                ),
            )
        for idx, (gen, exp) in enumerate(zip(generated, expected, strict=False)):
            error = find_json_mismatches(gen, exp, (*path, idx))
            if error:
                errors.append(error)
        if errors:
            return ExceptionGroup(pprint_path(path), errors)
    elif isinstance(expected, (str, bool, int, float, type(None))):
        # handle JSON types that aren't containers
        if expected != generated:
            return ValueError(
                f"{pprint_path(path)}\nvalue-mismatch: expected {expected!r}, generated {generated}",
            )
    else:
        return TypeError(f"{pprint_path(path)}: unexpected type: {type(generated)!r}")

    return None


def test_build_saml2_config(base_app: Flask) -> None:
    """Test invenio-edugain's building of pysaml2 config."""
    config_core = Pysaml2ConfigCore(
        server_domain_others=[  # this takes precedence over flask_config["EDUGAIN_OTHER_SERVER_DOMAINS"]
            "https://localhost:5000",  # add localhost (might wanna do this for testing)
            "https://demo.repository.foo.org",
        ],
        flask_config=sample_flask_config,  # take rest of values from flask-config
    )
    computed_config = build_pysaml2_config(base_app, config_core)

    error = find_json_mismatches(computed_config, expected_sample_config)
    if error:
        raise error
