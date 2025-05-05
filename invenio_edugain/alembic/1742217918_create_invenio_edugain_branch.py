# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create invenio_edugain branch."""

# revision identifiers, used by Alembic.
revision = "1742217918"
down_revision = None
branch_labels = ("invenio_edugain",)
depends_on = "dbdbc1b19cf2"


def upgrade() -> None:
    """Upgrade database."""


def downgrade() -> None:
    """Downgrade database."""
