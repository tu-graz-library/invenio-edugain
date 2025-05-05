# invenio-edugain

> [!WARNING]
> This package is not implemented yet.
>
> It's at the top of our priority list and actively being worked on though.

This package will implement an easy way to bring `edugain` logins to your invenio instance.

Planned features:

- discovery service that looks native to your invenio instance
- parse IdP-configuration from file/url (manually via CLI or on configurable timer)
- parsed IdP-configurations persist in database
- activate/deactivate some IdPs at your choice (e.g. if your security-team would like to allow IdPs only after taking a look at them)
- on discovery page, a configurable institution should be filled in per default
- configuration that's more ergonomic than having to write the whole frigging settings JSON

## Installation

Use your package installer to install `invenio_edugain`, e.g. via `pip`:

```bash
pip install invenio_edugain
```

When creating a new invenio instance, `invenio_edugain`'s SQL-tables will automatically be created with all the other tables.
When adding to an existing instance, you'll have to create the new SQL-tables used by `invenio_edugain` like so:

```bash
invenio alembic upgrade
```

## `invenio-jobs` integration

`invenio-edugain`'s idp-data ingestion can be run via the _jobs_ view in the administration UI.
Note that the _jobs_ view is hidden by default, enable it via adding the following configuration:

```python
JOBS_ADMINISTRATION_ENABLED = True
```

<!-- TODO: link to invenio-jobs documentation once it was written -->

## invenio-edugain at Invenio RDM Meeting 2025

Our team was present at the Invenio RDM Meeting 2025 ([invitation](https://herrner.github.io/irdm2025/), [indico](https://www.conferences.uni-hamburg.de/event/548/overview)).
One of the [discussed topics](https://uhh.de/fdm-irdm25) was edugain ([write-up](https://pad.uni-hamburg.de/zVH2FSxTTJeSIq6uHAUgGA#)).
This helped in getting a clearer handle on what people require of `invenio-edugain` and on how to implement it.

Many thanks to the people partaking in the discussion and to _Universität Hamburg_ for hosting the event.
