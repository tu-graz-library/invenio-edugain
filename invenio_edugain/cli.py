# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Graz University of Technology.
#
# invenio-edugain is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface for invenio-edugain."""

import re

from click import Context, argument, group, option, pass_context, secho, style
from flask.cli import with_appcontext
from invenio_db import db
from saml2.mdstore import InMemoryMetaData, MetadataStore

from . import ingest
from .models import IdPData
from .utils import load_mdstore


@group()
def edugain() -> None:
    """CLI-group for `invenio edugain` commands."""


@edugain.command("ingest")
@argument("metadata_xml_location")
@option("--xml-sig-cert")
@option("--cert-fingerprint-sha256")
@with_appcontext
def ingest_idps(
    metadata_xml_location: str,
    xml_sig_cert: str | None,
    cert_fingerprint_sha256: str | None,
) -> None:
    """Import IdP-configuration(s) from file/url.

    \b
    Examples:
      invenio edugain ingest ./saml-metadata.xml
      invenio edugain ingest
        https://url/to/saml-metadata.xml
        --xml-sig-cert https://url/to/cert
        --fingerprint '0A:1B:2C:3D:4E:5F:67:89:DE:AD:BE:EF:...'

    When ingesting from url, a signing cert is required.
    When getting cert from url, a fingerprint of the cert is required.
    """  # noqa: D301  # \b prevents click's line-wrapping
    mds = load_mdstore(
        metadata_xml_location,
        cert_location=xml_sig_cert,
        fingerprint_sha256=cert_fingerprint_sha256,
    )
    import_item = ingest.from_mdstore(mds)
    secho(
        f"Successfully imported idp-settings from {metadata_xml_location!r}\n"
        f"- {len(import_item.added_idp_ids)} added\n"
        f"- {len(import_item.updated_idp_ids)} updated\n"
        f"- {len(import_item.unchanged_idp_ids)} already up-to-date",
        fg="green",
    )


class MetadataLoader(InMemoryMetaData):
    """Loads idp-settings from SQL-db.

    This is akin to saml2.mdstore.MetaDataMD, which loads from file rather than from db.
    Also stores columns from IdPData table to its `.idp_data` attribute.
    """

    def __init__(self, attrc: tuple | None) -> None:
        """Init."""
        super().__init__(attrc)
        self.idp_data: dict[str, dict] = {}

    def load(self) -> None:
        """Load."""
        for idp in db.session.scalars(db.select(IdPData)):
            self.entity[idp.id] = idp.settings
            self.idp_data[idp.id] = {
                col.key: getattr(idp, col.key) for col in idp.__table__.columns
            }


@edugain.command()
@argument("regex")
@with_appcontext
def search(regex: str) -> None:
    """Search through ingested IdPs' names/urls to find matching IdPs.

    \b
    Examples:
      invenio edugain search 'university'
      invenio edugain search 'uni.*ity'
    """  # noqa: D301  # \b prevents click's line-wrapping
    pattern = re.compile(regex, flags=re.IGNORECASE)

    mds = MetadataStore(None, {})
    mdl = MetadataLoader(mds.attrc)
    mdl.load()
    mds.metadata["db"] = mdl

    matches = {}
    for idp_id in sorted(mds.identity_providers()):
        match_candidates = []
        match_candidates.extend(mds.mdui_uiinfo_display_name(idp_id))
        if name := mds.name(idp_id):
            match_candidates.append(name)
        uiinfos = list(mds.mdui_uiinfo(idp_id))
        match_candidates.extend(
            keyword_dict["text"]
            for uiinfo in uiinfos
            for keyword_dict in uiinfo.get("keywords", [])
        )
        if pattern.search(idp_id) or any(pattern.search(dn) for dn in match_candidates):
            matches[idp_id] = mdl.idp_data[idp_id]
            matches[idp_id]["match_info"] = match_candidates

    if not matches:
        secho(f"no results found for given reges {regex!r}", fg="yellow")
        return

    # echo table header
    max_id_len = max(len(idp_id) for idp_id in matches)
    secho(
        f"enabled discoverable idp-id{" " * (max_id_len - 4)}name0;name1;...;keyword0;...",
        bold=True,
    )
    for idp_id, idp_data in matches.items():
        match_info = idp_data["match_info"]
        enabled = idp_data["enabled"]
        discoverable = idp_data["discoverable"]
        enabled_chr = "O" if enabled else "X"
        enabled_str = style(
            enabled_chr.center(len("enabled")),
            fg="green" if enabled else "red",
        )
        disco_chr = "O" if discoverable else "X"
        disco_str = style(
            disco_chr.center(len("discoverable")),
            fg="green" if discoverable else "red",
        )
        secho(
            f"{enabled_str} {disco_str} {idp_id}{' '*(max_id_len-len(idp_id)+2)}{';'.join(match_info)}",
        )


@edugain.command()
@pass_context
@argument("idp-ids", nargs=-1)
@option("--disable", is_flag=True, default=False)
@option("--enable", is_flag=True, default=False)
@option("--hide", is_flag=True, default=False)
@option("--show", is_flag=True, default=False)
@with_appcontext
def manage(  # noqa: C901
    ctx: Context,
    idp_ids: tuple[str, ...],
    disable: bool,  # noqa: FBT001
    enable: bool,  # noqa: FBT001
    hide: bool,  # noqa: FBT001
    show: bool,  # noqa: FBT001
) -> None:
    """Manage given IdPs' configuration in db (enable/disble, show/hide).

    \b
    Examples:
      invenio edugain manage --enable --show idp-id-1 idp-id-2
      xargs -a whitelisted-idp_ids invenio edugain manage --enable
      generated-blacklist | xargs edugain manage --disable


    Choose actions out of `--disable`, `--enable`, `--hide`, `--show`
    and apply given actions to given IdPs.
    IdP-ids are in URI format and can be found via `invenio edugain search`.
    """  # noqa: D301  # \b prevents click's line-wrapping
    error_msgs: list[str] = []
    if not idp_ids:
        error_msgs.append("supply at least one idp-id to change")
    if disable and enable:
        error_msgs.append("--disable and --enable are mutually exclusive")
    if hide and show:
        error_msgs.append("--hide and --show are mutually exclusive")
    if not any([disable, enable, hide, show]):
        error_msgs.append(
            "command would have no effect, choose at least one action out of --disable, --enable, --hide, --show",
        )

    if error_msgs:
        msg = "\n".join(error_msgs)
        secho(msg, err=True, fg="red")
        ctx.exit(2)

    idps_data: dict[str, IdPData] = {
        idp_data.id: idp_data
        for idp_data in db.session.scalars(db.select(IdPData).order_by(IdPData.id))
    }
    if unknown_ids := set(idp_ids) - set(idps_data):
        msg = f"no idps were ingested for the following given ids: {sorted(unknown_ids)!r}"
        secho(msg, err=True, fg="red")
        ctx.exit(1)

    updated_ids = set()
    for idp_id in idp_ids:
        idp_data = idps_data[idp_id]
        if disable and idp_data.enabled:
            idp_data.enabled = False
            updated_ids.add(idp_id)
        if enable and not idp_data.enabled:
            idp_data.enabled = True
            updated_ids.add(idp_id)
        if hide and idp_data.discoverable:
            idp_data.discoverable = False
            updated_ids.add(idp_id)
        if show and not idp_data.discoverable:
            idp_data.discoverable = True
            updated_ids.add(idp_id)

    db.session.commit()
    secho(f"Updated {len(updated_ids)} IdPs", fg="green")
