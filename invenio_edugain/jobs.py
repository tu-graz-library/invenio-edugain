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


class ABSENT:
    """Sentinel distinct from `None`.

    Signifies that this argument was absent in function call.
    """


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
        metadata_xml_location: str | None | type[ABSENT] = ABSENT,
        cert_location: str | None | type[ABSENT] = ABSENT,
        fingerprint_sha256: str | None | type[ABSENT] = ABSENT,
        job_arg_schema: str | None = None,  # noqa: ARG003
    ) -> dict:
        """Generate arguments for task.

        Received arguments are `job_obj`, `since`, plus all fields in `arguments_schema`.
        """
        # this is called for two completely different purposes:
        #   1. to generate a reference configuration to show on the jobs panel
        #      in this case, only `job_obj`, `since` are passed
        #      (other args are ABSENT in this case)
        #   2. to calculate the arguments for executing the job
        #      in this case, all args are passed but may be `None`
        #      (since all args are passed in this case, non take the default value ABSENT)
        inputs = {
            "metadata_xml_location": metadata_xml_location,
            "cert_location": cert_location,
            "fingerprint_sha256": fingerprint_sha256,
        }
        if all(value is not ABSENT for value in inputs.values()):
            return inputs

        if all(value is ABSENT for value in inputs.values()):
            # this return is only displayed in the job's "configure and run" form as a reference configuration
            reference_configuration = {
                "metadata_xml_location": "https://my-local-edugain-federation-member.org/saml-metadata.xml",
                "cert_location": "https://my-local-edugain-federation-member/metadata-signing.crt",
                "fingerprint_sha256": "0A:1B:2C:3D:4E:5F:67:89:DE:AD:BE:EF:DE:AD:BE:EF:DE:AD:BE:EF:DE:AD:BE:EF:DE:AD:BE:EF:DE:AD:BE:EF",
            }
            return reference_configuration  # noqa: RET504

        msg = (
            "must either be called by providing *all* input arguments or *none* of them"
        )
        raise ValueError(msg)
