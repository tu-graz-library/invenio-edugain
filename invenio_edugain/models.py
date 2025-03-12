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
    # TODO: differentiate between displayname and search-string
    #       if org behind IdP has multiple alternate names:
    #          - can only display one name
    #          - but all names should be findable when searching with disco service
    # TODO: language-preference for displaynames
    displayname: Mapped[str]
    enabled: Mapped[bool] = mapped_column(default=False)
    logo_url: Mapped[str]
    # holds internal (i.e. already parsed by pysaml2) representation of idp-settings
    settings: Mapped[dict] = mapped_column(
        db.JSON().with_variant(JSONB(), "postgresql"),
    )

    def __repr__(self) -> str:
        """Repr."""
        return (
            f"{type(self).__qualname__}("
            f"id={self.id!r}, "
            f"displayname={self.displayname!r}, "
            f"enabled={self.enabled!r}, "
            f"logo_url={self.logo_url!r}, "
            "settings=...)"
        )
