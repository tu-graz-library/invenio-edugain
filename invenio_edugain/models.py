# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""SQL-table definitions for invenio-edugain."""

from invenio_db import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class IdPData(db.Model):
    """Flask-SQLAlchemy model for "edugain_idp_data" SQL-table."""

    __tablename__ = "edugain_idp_data"

    id: Mapped[str] = mapped_column(primary_key=True)
    discoverable: Mapped[bool] = mapped_column(default=True)
    enabled: Mapped[bool] = mapped_column(default=False)
    # holds internal (i.e. already parsed by pysaml2) representation of idp-settings
    settings: Mapped[dict] = mapped_column(
        db.JSON().with_variant(JSONB(), "postgresql"),
    )

    def __repr__(self) -> str:
        """Repr."""
        return (
            f"{type(self).__qualname__}("
            f"id={self.id!r}, "
            f"discoverable={self.discoverable!r}, "
            f"enabled={self.enabled!r}, "
            "settings=...)"
        )
