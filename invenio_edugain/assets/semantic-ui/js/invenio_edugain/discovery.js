// Copyright (C) 2025 Graz University of Technology.
//
// invenio-edugain is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { IdPSelectUI } from "@js/shibboleth_eds/idpselect.js";
import { IdPSelectUIParms } from "@js/shibboleth_eds/idpselect_config.js";

const IdPSelectElement = document.getElementById("idpSelect");

const backendEDSConfigText = IdPSelectElement?.dataset?.shibbolethEdsConfig || null;
const backendEDSConfig = backendEDSConfigText ? JSON.parse(backendEDSConfigText) : {};
const defaultEDSConfig = new IdPSelectUIParms();
const mergedEDSConfig = { ...defaultEDSConfig, ...backendEDSConfig };

new IdPSelectUI().draw(mergedEDSConfig);
