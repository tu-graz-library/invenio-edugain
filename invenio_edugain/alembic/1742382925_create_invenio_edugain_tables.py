# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create invenio_edugain tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1742382925"
down_revision = "1742217918"
branch_labels = ()
depends_on = None


def upgrade() -> None:
    """Upgrade database."""
    op.create_table(
        "edugain_idp_data",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("displayname", sa.String(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("logo_url", sa.String(), nullable=False),
        sa.Column(
            "settings",
            sa.JSON().with_variant(
                postgresql.JSONB(astext_type=sa.Text()),
                "postgresql",
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_edugain_idp_data")),
    )


def downgrade() -> None:
    """Downgrade database."""
    op.drop_table("edugain_idp_data")
