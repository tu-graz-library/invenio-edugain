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
#   ./run-tests.sh [-K|--keep-services] [pytest options and args...]
#
# Note: you can chose which db-service to run tests with via environment-variable `DB`
#       if not set, DB=postgresql is used as default
#
# Example for testing with mysql instead of postgresql:
#    DB=mysql ./run-tests.sh

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Check for arguments
keep_services=0
pytest_args=()
for arg in $@; do
    # from the CLI args, filter out some known values and forward the rest to "pytest"
    # note: we don't use "getopts" here b/c of some limitations (e.g. long options),
    #       which means that we can't combine short options (e.g. "./run-tests -Kk pattern")
    case ${arg} in
        # Note: lower-case `-k` would clash with "pytest"
        -K|--keep-services)
            keep_services=1
            ;;
        *)
            pytest_args+=( ${arg} )
            ;;
    esac
done

# if not --keep-services, then down services on exit
function cleanup {
    eval "$(docker-services-cli down --env)"
}
if [[ ${keep_services} -eq 0 ]]; then
    trap cleanup EXIT
fi


ruff check .
eval "$(docker-services-cli up --db ${DB:-postgresql} --env)"
python -m pytest ${pytest_args[@]+"${pytest_args[@]}"}
