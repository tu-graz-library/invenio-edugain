# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio jobs for invenio-edugain."""

from datetime import datetime

from invenio_jobs.jobs import JobType
from invenio_jobs.models import Job
from marshmallow import Schema, fields

from .tasks import ingest_idp_data


class IngestIdPDataArgsSchema(Schema):
    """Schema of input arguments for `IngestIdPDataJob`."""

    metadata_xml_location = fields.String(
        metadata={
            "description": "URL/filepath to xml with SAML metadata",  # TODO: translate
            # note that lodash.capitalize will be called on the title:
            "title": "SAML metadata location",  # TODO: translate
        },
        required=True,
    )
    cert_location = fields.String(
        allow_none=True,
        metadata={
            "description": "URL/filepath to certificate for SAML metadata (only necessary when loading metadata from url)",  # TODO: translate
            "title": "certificate location",  # TODO: translate
        },
    )
    fingerprint_sha256 = fields.String(
        allow_none=True,
        metadata={
            "description": "SHA256 fingerprint of the certificate (only necessary when loading certificate from url)",  # TODO: translate
            "title": "SHA256 fingerprint of cert",  # TODO: translate
        },
    )
    job_arg_schema = fields.String(
        metadata={"type": "hidden"},
        dump_default="IngestIdPDataArgsSchema",
        load_default="IngestIdPDataArgsSchema",
    )


class NOT_GIVEN:  # noqa: N801
    """Sentinel distinct from `None`."""


class IngestIdPDataJob(JobType):
    """Job for ingesting IdP data into database."""

    arguments_schema = IngestIdPDataArgsSchema
    description = "Ingests IdP data from given file/URL into db"  # TODO: translate
    id = "ingest_idp_data"
    task = ingest_idp_data
    title = "Ingest IdP data"  # TODO: translate

    @classmethod
    def build_task_arguments(
        cls,
        job_obj: Job,  # noqa: ARG003
        since: datetime | None = None,  # noqa: ARG003
        metadata_xml_location: str | None | type[NOT_GIVEN] = NOT_GIVEN,
        cert_location: str | None | type[NOT_GIVEN] = NOT_GIVEN,
        fingerprint_sha256: str | None | type[NOT_GIVEN] = NOT_GIVEN,
        job_arg_schema: str | None = None,  # noqa: ARG003
    ) -> dict:
        """Generate arguments for task.

        Received arguments are `job_obj`, `since`, plus all fields in `arguments_schema`.
        """
        # this is called for two different purposes:
        #   1. to generate a reference configuration to show on the jobs panel
        #      in this case, only `job_obj`, `since` are passed
        #      (other args are set to NOT_GIVEN in this case)
        #   2. to calculate the arguments for executing the job
        #      in this case, all args are passed but may be `None`
        #      (since all args are passed in this case, non take the default value NOT_GIVEN)
        metadata_xml_location = (
            metadata_xml_location
            if metadata_xml_location is not NOT_GIVEN
            else "https://mds.edugain.org/edugain-v2.xml"
        )
        cert_location = (
            cert_location
            if cert_location is not NOT_GIVEN
            else "https://technical.edugain.org/mds-v2.cer"
        )
        fingerprint_sha256 = (
            fingerprint_sha256
            if fingerprint_sha256 is not NOT_GIVEN
            else "BD:21:40:48:9A:9B:D7:40:44:DD:68:05:34:F7:78:88:A9:C1:3B:0A:C1:7C:4F:3A:03:6E:0F:EC:6D:89:99:95"
        )
        return {
            "metadata_xml_location": metadata_xml_location,
            "cert_location": cert_location,
            "fingerprint_sha256": fingerprint_sha256,
        }
