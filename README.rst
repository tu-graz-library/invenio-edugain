# invenio-edugain

> [!NOTE]
> Most of this package is licensed under the MIT license.
> However, it also contains code from _Shibboleth Consortium_, which is licensed under Apache 2.0.
> This is explicitly mentioned in file-headers where applicable.
> An Apache 2.0 license is provided in the relevant subdirectory.

> [!WARNING]
> This package is not implemented yet.
>
> It's at the top of our priority list and actively being worked on though.

`invenio-edugain` implements an easy way to add login via edugain to your invenio instance.

## Contents of this README

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
  - [SAML (i.e. the underlying authentication-data exchange protocol)](#configuration-of-saml)
  - [Discovery service (i.e. the _select your institution_ webpage)](#configuration-of-discovery-service)

## Features

- discovery service (i.e. a _Select your institution to login with_ webpage)
- load metadata (i.e. name/cryptographic credentials of other institutions) via `invenio-jobs`
- choose which other institutions may be used to login from (enable/disable them)
- configuration
  - included config-building machinery can build basic configuration
  - for advanced use cases, all configuration fields of the underlying `pysaml2` and `shibboleth EDS` are accessible

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

## Configuration

### Configuration of SAML

To securely exchange authentication data, _edugain_ uses the SAML protocol.
`invenio-edugain` uses for its SAML protocol implementation `pysaml2`.
The important thing when configuring `pysaml2` is this:

> _After app-finalization, `app.config["EDUGAIN_PYSAML2_CONFIG"]` MUST be a valid `pysaml2` config dict._
>
> (we don't care _how_ you compute the `pysaml2` config - hardcoding, using config-builder, computing it yourself, or any combination thereof will work - just remember to set the computed config to `EDUGAIN_PYSAML2_CONFIG` before app-finalization)

For available configuration fields, see [`pysaml2` docs](https://pysaml2.readthedocs.io/en/latest/howto/config.html).  
For ways to setup a `pysaml2` configuration, read on.

Per default, `invenio-edugain` attempts to setup `EDUGAIN_PYSAML2_CONFIG` automatically from some `EDUGAIN_*` config-vars.
Start your invenio-instance with `invenio-edugain` installed and it will show missing config-vars.

Alternatively, you may turn off automatic setup of `EDUGAIN_PYSAML2_CONFIG` (and set it yourself instead)
by setting `EDUGAIN_PYSAML2_CONFIG_BUILDING_ENABLED` to `False` (in your `invenio.cfg` file).
In this case, you may re-use config-building machinery:

```python
# Example: build `pysaml2` config yourself rather than automatically

##
## in invenio.cfg
##
EDUGAIN_PYSAML2_CONFIG_BUILDING_ENABLED = False

##
## in an app-finalization entry-point
##
from invenio_edugain.build_config import build_pysaml2_config, Pysaml2ConfigCore, Pysaml2ConfigCoreContacts

def finalize_app(app):
    # first, build a config-core (consisting of the fields for which no defaults can be given)
    config_core = Pysaml2ConfigCore(
        service=Pysaml2ConfigCoreContacts(
            security_contact_email="support@my-invenio-instance.org",
            security_contact_given_name="ZID",
            security_contact_surname="(IT support)",
            technical_support_email=compute_technical_support_email_somehow(),
            technical_support_given_name="Technical",
            technical_support_surname="Support",
        ),
        server_domain_main="my-invenio-instance.org",  # main domain this service runs on
        server_domain_others=[  # other domains that serve the same service (e.g. demo-, test-servers)
            "demo.my-invenio-instance.org",
            "my-invenio-test-instance.org",
        ],
        flask_config=app.config,  # arguments not provided above (if any) are taken from flask_config (if provided)
    )

    # second, expand the config-core into a full `pysaml2` config
    pysaml2_config = build_pysaml2_config(app=app, config_core=config_core)

    # optional (advanced): change some fields of the parts of the built `pysaml2` config
    pysaml2_config["logging"] = {...}

    # don't forget to set `EDUGAIN_PYSAML2_CONFIG`
    app.config["EDUGAIN_PYSAML2_CONFIG"] = pysaml2_config
```

You can also set the full config by hand rather than going through config-builder machinery:

```python
# Example: statically set `EDUGAIN_PYSAML2_CONFIG`

##
## in invenio.cfg
##
EDUGAIN_PYSAML2_CONFIG_BUILDING_ENABLED = False
EDUGAIN_PYSAML2_CONFIG = {...}  # set to a pysaml2 config-dict
```

### Configuration of discovery service

Users need to be able to select the institution they wish to login with.
A webpage on which users can make such selection is called a _discovery service_.
`invenio-edugain` vendors _`shibboleth-EDS` (embedded discovery service)_ for this.
The important thing when configuring `shibboleth-EDS` is this:

> _After app-finalization, `app.config["EDUGAIN_SHIBBOLETH_EDS_CONFIG"]` MUST be a valid shibboleth-eds config dict._
>
> (we don't care _how_ you compute the `shibboleth-EDS` config - hardcoding, using config-builder, computing it yourself, or any combination thereof will work - just remember to set the computed config to `EDUGAIN_SHIBBOLETH_EDS_CONFIG` before app-finalization)

For available configuration fields, see [`shibboleth-EDS` docs](https://shibboleth.atlassian.net/wiki/spaces/EDS10/pages/2383446048/3.2+EDS+Configuration+Options).  
For defaults, see the vendored [`idpselect_config.js`](./invenio_edugain/assets/semantic-ui/shibboleth-embedded-ds-1.3.0/nonminimised/idpselect_config.js) (note that the configuration-field `selectedLanguage` is instead controlled via `current_i18n.language`).  
For ways to setup a `shibboleth-EDS` config, read on.

Per default, `invenio-edugain` automatically sets up a basic `EDUGAIN_SHIBBOLETH_EDS_CONFIG`.  
When using automatic building, `EDUGAIN_SHIBBOLETH_EDS_CONFIG_KWARGS` can be used to selectively overwrite config-fields.

```python
# Example: overwrite some fields of shibboleth-config

##
## in invenio.cfg
##
EDUGAIN_SHIBBOLETH_EDS_CONFIG_KWARGS = {
    "preferredIdP": ["https://login.institution.org/idp/"],  # always suggest these institutions to user
}
```

Alternatively, you may turn off automatic setup of `EDUGAIN_SHIBBOLETH_EDS_CONFIG` (and set it yourself instead)
by setting `EDUGAIN_SHIBBOLETH_EDS_CONFIG_BUILDING_ENABLED` to `False` (in your invenio.cfg file).  
In that case, set `EDUGAIN_SHIBBOLETH_EDS_CONFIG` yourself.
You may (but need not) re-use config-builder machinery for this:

```python
# Example: build `shibboleth-EDS` config yourself rather than automatically

##
## in invenio.cfg
##
EDUGAIN_SHIBBOLETH_EDS_CONFIG_BUILDING_ENABLED = False

##
## in an app-finalization entry-point
##
from invenio_edugain.build_config import build_shibboleth_eds_config

def finalize_app(app):
    shibboleth_eds_config = build_shibboleth_eds_config(
        app,
        preferredIdP=["https://login.institution.org/idp/"],
        # further config-fields here
    )

    # don't forget to set `EDUGAIN_SHIBBOLETH_EDS_CONFIG`
    app.config["EDUGAIN_SHIBBOLETH_EDS_CONFIG"] = shibboleth_eds_config
```

## `invenio-jobs` integration

`invenio-edugain`'s idp-data ingestion can be run via the _jobs_ view in the administration UI.
Note that the _jobs_ view is hidden by default, enable it via adding the following configuration:

```python
JOBS_ADMINISTRATION_ENABLED = True
```

<!-- TODO: link to invenio-jobs documentation once it was written -->

## translations

For extracting messages into a .pot file:

1. make sure your current python environment has the `babel` package installed  
   (`babel` is part of the `invenio` stack - your invenio virtual-environment should work)

2. find the current `invenio-edugain` version in `./invenio-edugain/__init__.py`  
   (the value of the `version` variable near the top of the file)

3. run the following command with `--version` set to the current version of `invenio-edugain`:

```bash
pybabel extract --copyright-holder "Graz University of Technology" --mapping-file pyproject.toml --output-file invenio_edugain/translations/messages.pot --add-comments NOTE --project invenio-edugain --version "<version here>" invenio_edugain/
```

For now, `babel` commands cannot be configured via `pyproject.toml`, so arguments need be provided as `--arg`.  
There's an open `babel` issue for adding `pyproject.toml` support: [link](https://github.com/python-babel/babel/issues/777)

## invenio-edugain at Invenio RDM Meeting 2025

Our team was present at the Invenio RDM Meeting 2025 ([invitation](https://herrner.github.io/irdm2025/), [indico](https://www.conferences.uni-hamburg.de/event/548/overview)).
One of the [discussed topics](https://uhh.de/fdm-irdm25) was edugain ([write-up](https://pad.uni-hamburg.de/zVH2FSxTTJeSIq6uHAUgGA#)).
This helped in getting a clearer handle on what people require of `invenio-edugain` and on how to implement it.

Many thanks to the people partaking in the discussion and to _Universität Hamburg_ for hosting the event.
