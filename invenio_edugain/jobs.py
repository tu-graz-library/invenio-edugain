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

    file_or_url = fields.String(
        metadata={
            "description": "URL/filepath to xml with SAML metadata",  # TODO: translate
            # note that lodash.capitalize will be called on the title:
            "title": "URL / filepath",  # TODO: translate
        },
        required=True,
    )
    job_arg_schema = fields.String(
        metadata={"type": "hidden"},
        dump_default="IngestIdPDataArgsSchema",
        load_default="IngestIdPDataArgsSchema",
    )


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
        file_or_url: str | None = None,
        job_arg_schema: str | None = None,  # noqa: ARG003
    ) -> dict:
        """Generate arguments for task.

        Received arguments are `job_obj`, `since`, plus all fields in `arguments_schema`.
        """
        # this is also called to calculate reference configuration for this job
        # in that case, args (except for `job_obj`, `since`) are `None`
        file_or_url = (
            file_or_url
            if file_or_url is not None
            else "https://mds.edugain.org/edugain-v2.xml"  # TODO: make configurable once flask-extension initialization exists
        )
        return {
            "file_or_url": file_or_url,
        }
