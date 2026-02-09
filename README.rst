===============
invenio-edugain
===============

.. pull-quote::
  [!NOTE]
  Most of this package is licensed under the MIT license.
  However, it also contains code from *Shibboleth Consortium*, which is licensed under Apache 2.0.
  This is explicitly mentioned in file-headers where applicable.
  An Apache 2.0 license is provided in the relevant subdirectory.

`invenio-edugain` implements an easy way to add login via edugain to your invenio instance.

Contents of this README
=======================

- `Overview of edugain`_
- `Features`_
- `Setup`_
- `Advanced Configuration`_

Overview of edugain
-------------------

To fill in the form for registering your invenio instance for use with edugain, it's necessary to have basic knowledge about terminology and inner workings.
This section quickly summarizes that.

**Secure Assertion Markup Language (SAML)**: a standard for authenticating users, build on XML

By SAML's HTTP-POST protocol, authentication involves two servers and a user, and works as follows:

1. user wants to log into server #1
2. on the server #1 website, user choses to authenticate themselves via server #2
3. server #1 redirects user to server #2's login page (the redirect contains a SAML authentication request as URL parameter)
4. user authenticates themselves on server #2
5. server #2 builds a SAML authentication response and makes user POST that to server #1
6. the authentication response includes email/name/... (encryptedly) which allows server #1 to log in the user

- **Service Provider (SP)**: within the above protocol, the party that sends SAML authentication requests (i.e. server #1)
- **Identity Provider (IdP)**: within the above protocol, the party that responds to SAML authentication requests with SAML authentication responses (i.e. server #2)
- **Identity Federation**: a federation of multiple organizations, each of which provides identit(ies) and/or service(s) (i.e. a bunch of orgs, all of which run an SP server and/or IdP server)
- **Inter-Federation**: a federation made up of multiple different federations
- **edugain**: an inter-federation of >80 federations, containing >8000 IdPs/SPs between its members

Features
--------

- discovery service (i.e. a *Select your institution to login with* webpage)
- load metadata (i.e. name/cryptographic credentials of other institutions) via `invenio-jobs`
- choose which other institutions may be used to login from (enable/disable them)
- configuration
  - included config-building machinery can build basic configuration
  - for advanced use cases, all configuration fields of the underlying `pysaml2` and `shibboleth EDS` are accessible

Setup
-----

**1. install the package, its tables, and its assets**

Use your package installer to install `invenio_edugain`, e.g. via `pip`:

.. code-block:: bash

   pip install invenio_edugain


Use `invenio-cli` to rebuild assets s.t. `invenio-edugain`'s assets are built:

.. code-block:: bash

   invenio-cli assets build


When creating a new invenio instance, `invenio_edugain`'s SQL-tables will automatically be created with all the other tables.
When adding to an existing instance, you'll have to create the new SQL-tables used by `invenio_edugain` like so:

.. code-block:: bash

   invenio alembic upgrade


**2. provide necessary configuration**

The following MUST be configured before `invenio-edugain` is usable:

+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| config variable name                       | example values                                                                      | notes                                                                                                                                                                                                                                                                                       |
+============================================+=====================================================================================+=============================================================================================================================================================================================================================================================================================+
| `EDUGAIN_GEANT_COC_COMPLIANT`              | `True`, `False`                                                                     | claims compliance with [GÉANT's *data protection code of conduct*](https://geant3plus.archive.geant.net/Documents/GEANT_DP_CoC_ver1.0.pdf)<br>some IdPs will only work if this is set<br>note that this may have legal consequences, so make sure your service complies before setting this |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_REFEDS_COMPLIANT`                 | `True`, `False`                                                                     | claims compliance with [REFEDS's *research and scholarship*](https://refeds.org/category/research-and-scholarship)<br>educational institutions will want this<br>note that this may have legal consequences, so make sure your service complies before setting this                         |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_CONTACT_SECURITY_EMAIL`           | `"repository-support@foo.org"`                                                      | for security incident response                                                                                                                                                                                                                                                              |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_CONTACT_SECURITY_GIVEN_NAME`      | `"Security"`                                                                        | for security incident response                                                                                                                                                                                                                                                              |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_CONTACT_SECURITY_SUR_NAME`        | `"Contact"`                                                                         | for security incident response                                                                                                                                                                                                                                                              |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_CONTACT_SUPPORT_EMAIL`            | `"repository-support@foo.org"`                                                      | for technical support                                                                                                                                                                                                                                                                       |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_CONTACT_SUPPORT_GIVEN_NAME`       | `"Technical"`                                                                       | for technical support                                                                                                                                                                                                                                                                       |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_CONTACT_SUPPORT_SUR_NAME`         | `"Support"`                                                                         | for technical support                                                                                                                                                                                                                                                                       |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_ENCRYPTION_CERT`                  | `"/abs/path/to/encryption.crt"`, `"rel/path/to/encryption.crt"`                     | see [below](#3-create-certificates-for-secure-data-exchange)                                                                                                                                                                                                                                |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_ENCRYPTION_KEY`                   | `"/path/to/encryption.key"`                                                         | see [below](#3-create-certificates-for-secure-data-exchange)                                                                                                                                                                                                                                |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_SIGNING_CERT`                     | `"/path/to/signing.crt"`                                                            | see [below](#3-create-certificates-for-secure-data-exchange)                                                                                                                                                                                                                                |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_SIGNING_KEY`                      | `"/path/to/signing.key"`                                                            | see [below](#3-create-certificates-for-secure-data-exchange)                                                                                                                                                                                                                                |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_ORG_DISPLAYNAMES_BY_LANG`         | `{"en": "Foo University"}`                                                          | provide at least english                                                                                                                                                                                                                                                                    |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_ORG_NAMES_BY_LANG`                | `{"en": "Foo University"}`                                                          | provide at least english                                                                                                                                                                                                                                                                    |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_ORG_URLS_BY_LANG`                 | `{"en": "https://www.foo.org"}`                                                     | provide at least english                                                                                                                                                                                                                                                                    |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_MAIN_SERVER_DOMAIN`               | `"https://repo.foo.org"`                                                            |                                                                                                                                                                                                                                                                                             |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_OTHER_SERVER_DOMAINS`             | `["https://test.repo.foo.org"]`                                                     |                                                                                                                                                                                                                                                                                             |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_SERVICE_DESCRIPTION_EN`           | `"The Foo Repository is ..."`                                                       |                                                                                                                                                                                                                                                                                             |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_SERVICE_NAME_EN`                  | `"Foo Repository"`                                                                  |                                                                                                                                                                                                                                                                                             |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_UIINFO_DESCRIPTIONS_BY_LANG`      | `{"en": "The Foo Repo..."}`                                                         | provide at least english                                                                                                                                                                                                                                                                    |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_UIINFO_DISPLAYNAMES_BY_LANG`      | `{"en": "Foo Repository"}`                                                          | provide at least english                                                                                                                                                                                                                                                                    |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_UIINFO_LOGOS`                     | `[{"height": "177", "width": "177",`<br>`"text": "https://repo.foo.org/logo.png"}]` | provide at least one logo with `height == width`<br>logo-dict may have a `"lang"` key, in that case provide at least one logo without `"lang"` or one logo with `"lang": "en"`                                                                                                              |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_UIINFO_PRIVACY_URLS_BY_LANG`      | `{"en": "https://repo.foo.org/GDPR_en.pdf"}`                                        | provide at least english                                                                                                                                                                                                                                                                    |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_UIINFO_INFO_URLS_BY_LANG`         | `{"en": "https://repo.foo.org/"}`                                                   | provide at least english                                                                                                                                                                                                                                                                    |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EUDGAIN_ALLOW_IMGSRC_CSP`                 | `True`, `False`                                                                     | whether to allow showing logos on *choose your institution to log in with* page<br>this requires a CSP update, so you have to opt into it                                                                                                                                                   |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| `EDUGAIN_DISCOVERY_ADDITION_REQUEST_EMAIL` | `"support@repo.foo.org"`, `None`                                                    | shown on *choose your on institution* page as contact for requesting an organization be made loginable-with<br>set to `None` to turn this off                                                                                                                                               |
+--------------------------------------------+-------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**3. create certificates for secure data exchange**

Trust in these certificates is established by your local edugain representative checking them before distributing them to IdPs.
Thus self-signed certificates suffice.
The following command creates pairs of self-signed public/private keys.
Do note that some edugain representatives make additional requirements for this, e.g. Germany's DFN-AAI requires `-days` be at most 5 years.
Also note that your organization's security policies might add requirements for this.

.. code-block:: bash

    openssl req -x509 -new -newkey rsa:4096 -noenc -keyout encryption.key -out encryption.crt -days 3650
    openssl req -x509 -new -newkey rsa:4096 -noenc -keyout siginng.key    -out signing.crt    -days 3650


.. pull-quote::
  [!NOTE]
  When generating certificates with above command, you will be asked for some additional metadata.
  These certificates will be wrapped in SAML XML - which adds metadata from above configuration.
  Metadata you input here will be ignored in favor of that.
  Best practice is to blank most fields (by entering `.`), except for
  the CN field - which must be given, for that use your server's FQDN (e.g. `repo.foo.org`)

**4. ingest IdP metadata**

To authenticate via some IdP, we need to ingest their metadata.
Metadata of edugain's IdPs is provided under some URL by your local edugain representative.

Find the representative responsible for your area at [https://technical.edugain.org/status](https://technical.edugain.org/status).
Then find the metadata URL on your represenative's website.

`invenio-edugain`'s metadata ingestion can be run via the _jobs_ view in the administration UI:
1. create a new job for the task `edugain/SAML: ingest identity provider data`, check `Active`
2. edit the created job and fill in the args `Saml metadata location`, `Certificate location`, and `Sha256 fingerprint of cert` (all of them should be shown on the same webpage as the metadata URL)
3. schedule the job to run at least once per day

**5. register your service with edugain**

Registration procedure differs widely depending on your local edugain representative, and information is often spread over multiple web-sites.
Hence it's probably easiest to contact your representative via email and ask for guidance.
Ask them about the procedure/requirements to _register your service as a new Service Provider (SP)_.

Find your local edugain-representative (amd their contact email) here: [https://technical.edugain.org/status](https://technical.edugain.org/status)

At some point, they will likely require your configuration in form of a `SAML metadata XML`.
After correct configuration, such XML is made available under the URL `<host>/saml/sp/xml` (per default at least - overwritable with `EDUGAIN_ROUTES["sp-xml"]`).

Advanced Configuration
----------------------

**Configuration of SAML**

To securely exchange authentication data, _edugain_ uses the SAML protocol.
`invenio-edugain` uses for its SAML protocol implementation `pysaml2`.
The important thing when configuring `pysaml2` is this:

.. pull-quote::
  _After app-finalization, `app.config["EDUGAIN_PYSAML2_CONFIG"]` MUST be a valid `pysaml2` config dict._

  (we don't care _how_ you compute the `pysaml2` config - hardcoding, using config-builder, computing it yourself, or any combination thereof will work - just remember to set the computed config to `EDUGAIN_PYSAML2_CONFIG` before app-finalization)

For available configuration fields, see [`pysaml2` docs](https://pysaml2.readthedocs.io/en/latest/howto/config.html).
For ways to setup a `pysaml2` configuration, read on.

Per default, `invenio-edugain` attempts to setup `EDUGAIN_PYSAML2_CONFIG` automatically from some `EDUGAIN_*` config-vars.
Start your invenio-instance with `invenio-edugain` installed and it will show missing config-vars.

Alternatively, you may turn off automatic setup of `EDUGAIN_PYSAML2_CONFIG` (and set it yourself instead)
by setting `EDUGAIN_PYSAML2_CONFIG_BUILDING_ENABLED` to `False` (in your `invenio.cfg` file).
In this case, you may re-use config-building machinery:

.. code-block:: python

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


You can also set the full config by hand rather than going through config-builder machinery:

.. code-block:: python

   # Example: statically set `EDUGAIN_PYSAML2_CONFIG`

   ##
   ## in invenio.cfg
   ##
   EDUGAIN_PYSAML2_CONFIG_BUILDING_ENABLED = False
   EDUGAIN_PYSAML2_CONFIG = {...}  # set to a pysaml2 config-dict


**Configuration of discovery service**

Users need to be able to select the institution they wish to login with.
A webpage on which users can make such selection is called a *discovery service*.
`invenio-edugain` vendors *`shibboleth-EDS` (embedded discovery service)* for this.
The important thing when configuring `shibboleth-EDS` is this:

.. pull-quote::
  _After app-finalization, `app.config["EDUGAIN_SHIBBOLETH_EDS_CONFIG"]` MUST be a valid shibboleth-eds config dict._

  (we don't care _how_ you compute the `shibboleth-EDS` config - hardcoding, using config-builder, computing it yourself, or any combination thereof will work - just remember to set the computed config to `EDUGAIN_SHIBBOLETH_EDS_CONFIG` before app-finalization)

For available configuration fields, see [`shibboleth-EDS` docs](https://shibboleth.atlassian.net/wiki/spaces/EDS10/pages/2383446048/3.2+EDS+Configuration+Options).
For defaults, see the vendored [`idpselect_config.js`](./invenio_edugain/assets/semantic-ui/shibboleth-embedded-ds-1.3.0/nonminimised/idpselect_config.js) (note that the configuration-field `selectedLanguage` is instead controlled via `current_i18n.language`).
For ways to setup a `shibboleth-EDS` config, read on.

Per default, `invenio-edugain` automatically sets up a basic `EDUGAIN_SHIBBOLETH_EDS_CONFIG`.
When using automatic building, `EDUGAIN_SHIBBOLETH_EDS_CONFIG_KWARGS` can be used to selectively overwrite config-fields.

.. code-block:: python

   # Example: overwrite some fields of shibboleth-config

   ##
   ## in invenio.cfg
   ##
   EDUGAIN_SHIBBOLETH_EDS_CONFIG_KWARGS = {
       "preferredIdP": ["https://login.institution.org/idp/"],  # always suggest these institutions to user
   }


Alternatively, you may turn off automatic setup of `EDUGAIN_SHIBBOLETH_EDS_CONFIG` (and set it yourself instead)
by setting `EDUGAIN_SHIBBOLETH_EDS_CONFIG_BUILDING_ENABLED` to `False` (in your invenio.cfg file).
In that case, set `EDUGAIN_SHIBBOLETH_EDS_CONFIG` yourself.
You may (but need not) re-use config-builder machinery for this:

.. code-block:: python

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


**Translations**

For extracting messages into a .pot file:

1. make sure your current python environment has the `babel` package installed  (`babel` is part of the `invenio` stack - your invenio virtual-environment should work)
2. find the current `invenio-edugain` version in `./invenio-edugain/__init__.py` (the value of the `version` variable near the top of the file)
3. run the following command with `--version` set to the current version of `invenio-edugain`:

.. code-block:: bash

   pybabel extract --copyright-holder "Graz University of Technology" --mapping-file pyproject.toml --output-file invenio_edugain/translations/messages.pot --add-comments NOTE --project invenio-edugain --version "<version here>" invenio_edugain/


For now, `babel` commands cannot be configured via `pyproject.toml`, so arguments need be provided as `--arg`.
There's an open `babel` issue for adding `pyproject.toml` support: [link](https://github.com/python-babel/babel/issues/777)

Invenio RDM Partner Meetings
----------------------------

**invenio-edugain at Invenio RDM Meeting 2025**

Our team was present at the Invenio RDM Meeting 2025 ([invitation](https://herrner.github.io/irdm2025/), [indico](https://www.conferences.uni-hamburg.de/event/548/overview)).
One of the [discussed topics](https://uhh.de/fdm-irdm25) was edugain ([write-up](https://pad.uni-hamburg.de/zVH2FSxTTJeSIq6uHAUgGA#)).
This helped in getting a clearer handle on what people require of `invenio-edugain` and on how to implement it.

Many thanks to the people partaking in the discussion and to *Universität Hamburg* for hosting the event.
