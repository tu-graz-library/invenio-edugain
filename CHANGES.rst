Changes
=======

Version v0.2.2 (released 2026-02-12)

- fix(alembic): default wasn't enough

Version v0.2.1 (released 2026-02-12)

- fix(alembic): not applicable script

Version v0.2.0 (released 2026-02-10)

- fix: readme after changing to rst
- feat: implement translations
- feat: add cli for IdP management
- feat: add step-by-step instructions to readme

Version v0.1.0 (released 2026-02-09)

- chore(setup): bump dependencies
- chore(fix): rename md to rst files
- fix: update new default in expected test-result
- feat: tell user how to add their org to loginables
- fix: set allowed skew to recommended default
- feat: make configurable authn-response handling
- feat: make configurable discovery-page template
- feat: make configurable which CSS is used
- feat: lower missing config from error to warning
- fix(typing): favor correct type over LSP output
- fix: update formatting to new black version 26.1.0
- fix: add lxml dependency to tests
- tests: add test for building pysaml2 config
- disco-page: add fallback for when no logos given
- user-creation: fail early for better error-msg
- authn-parsing: update various things
- typing: unify two ABSENT implementations
- config-builder: rename variable for clarity
- update use `.getfoo` methods over property access
- fix: typing
- exception: rename for clarity
- jobs: update job title for clarity
- endpoints: improve error-messages
- task: add logging to `ingest_idp_data`
- typing: mark EDS-config fields as optional
- shibboleth-eds: check for version upgrades
- shibboleth-eds: upgrade vendored version to 1.4.0
- disco-feed: add language to logo-metadata
- endpoints: sanitize redirect URLs
- documentation: improve wording, add comment
- pyproject.toml: update license field to new format
- db: update models to distinguish visible/enabled
- readme: add index and configuration documentation
- fix: clarify `TupleJSON`, set "logging" to `None`
- config-builder: link up automatic building
- config-builder: add pysaml2 config builder
- config-builder: add pysaml2 config-core builder
- config-builder: add shibboleth-eds config builder
- fix: add to conftest fixture necessary config-var
- fix: guarantee existence and dict-ness of keys
- fix: remove old email-parsing
- CSS: add CSS for disco-page
- config: parse paths to crypto key-files from env
- user-creation: use random username instead
- fix: type-annotation
- disco-page: add opt-in into allowing loading logos
- fix: new name for `"id"`
- fix: XML encoding
- saml: multiplex when multiple ACS are configured
- fix: affiliations-delimiter should be `;` not `\n`
- gitignore: ignore npm lock-files
- ruff: change configuration
- disco: change old list-of-idps endpoint to new one
- configurability: make shibboleth-eds configurable
- html: replace home-brewn disco with shibboleth-eds
- eslint: fix issues eslint has with shibboleth-eds
- cleanup: delete unneeded files
- fix: change line-endings from \r\n to \n
- fix: mark variable as unused to satisfy ruff
- format: format shibboleth-eds files with prettier
- legal: add legal notes/headers for shibboleth-eds
- dependency: add shibboleth EDS
- ingest: clarify digital signature checking code
- ingest: check digital signature of pulled metadata
- setup: bump invenio-jobs
- fix: accomodate new ruff rules
- python: bump minimum version for better `typing`
- endpoints: add assertion consumer service
- views: add enpdoint for showing SP's metadata-XML
- views: add view for requesting authn from IdP
- utils: add pysaml2 loader for idp-metadata from db
- github CI: add linting for javascript
- js: add configuration for tools
- webpack: add webpack-configuration
- react: add dropdown for searching through IdPs
- views: add view for IdP discovery page
- html: add template for login-discovery
- static: add edugain icons
- utils: add utility for getting idp-data as dict
- flask: add configurability
- fix: fix parent-revision of alembic branch
- fix: itertools.chain `[name]` rather than `name`
- fix: add configuration for tests
- docs: add results of invenio RDM Meeting 2025
- ext: register package as flask-extension
- dependencies: upgrade minimum python version
- fix: add search-extras so tests can install them
- add integration with invenio-jobs
- add celery-task for ingesting idp-data
- tests: remove `live_server_scope` configuration
- tests: add python3.13 to test-matrix
- tests: add alembic test
- alembic: add initial revisions
- tests: add testing of data-ingestion
- db: add data ingestion of idp-data
- db: add idp-data model, add entry-point to models

Version v0.0.1 (release 2025-03-10)

package: initial commit
setup: base configuration

