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

## Installation

Use your package installer to install `invenio_edugain`, e.g. via `pip`:

```bash
pip install invenio_edugain
```

When adding to an existing instance, you'll have to create the new SQL-tables used by `invenio_edugain`:

```bash
invenio db create
```
