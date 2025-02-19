#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2022-2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Usage
#   ./run-tests.sh [pytest options and args...]

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Check for arguments
pytest_args=()
for arg in $@; do
    pytest_args+=( ${arg} )
done

ruff check .
python -m pytest ${pytest_args[@]+"${pytest_args[@]}"}
