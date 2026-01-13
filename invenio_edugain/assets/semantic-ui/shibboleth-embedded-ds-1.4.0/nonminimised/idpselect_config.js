/* Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// Changes by Graz University of Technology:
//   - add legal header
//   - format with prettier
//   - add `export` qualifiers
//   - fix escaping of regexp-strings

/** @class IdP Selector UI */
export function IdPSelectUIParms() {
  //
  // Adjust the following to fit into your local configuration
  //
  this.alwaysShow = true; // If true, this will show results as soon as you start typing
  this.dataSources = ["/Shibboleth.sso/DiscoFeed"]; // Where to get the data from (in an array)
  this.defaultLanguage = "en"; // Language to use if the browser local doesnt have a bundle
  this.selectedLanguage = null; // Set this to override the browser default (for instance if you can
  // detect this from the URL.
  this.defaultLogo = "blank.gif"; // Replace with your own logo
  this.defaultLogoWidth = 1;
  this.defaultLogoHeight = 1;
  this.defaultReturn = null; // If non null, then the default place to send users who are not
  // Approaching via the Discovery Protocol for example
  //this.defaultReturn = "https://example.org/Shibboleth.sso/DS?SAMLDS=1&target=https://example.org/secure";
  this.defaultReturnIDParam = null;
  this.redirectAllow = [
    "^https://example\\.org/Shibboleth\\.sso/Login.*$",
    "^https://example\\.com/Shibboleth\\.sso/Login.*$",
  ];
  this.helpURL = "https://wiki.shibboleth.net/confluence/display/SHIB2/DSRoadmap";
  this.ie6Hack = null; // An array of structures to disable when drawing the pull down (needed to
  // handle the ie6 z axis problem
  this.insertAtDiv = "idpSelect"; // The div where we will insert the data
  this.maxResults = 10; // How many results to show at once or the number at which to
  // start showing if alwaysShow is false
  this.myEntityID = null; // If non null then this string must match the string provided in the DS parms
  this.preferredIdP = null; // Array of entityIds to always show
  this.hiddenIdPs = null; // Array of entityIds to delete
  this.ignoreKeywords = false; // Do we ignore the <mdui:Keywords/> when looking for candidates
  this.showListFirst = false; // Do we start with a list of IdPs or just the dropdown
  this.samlIdPCookieTTL = 730; // in days, this cookie is used to offer previously chosen IDP as preferredIdP
  this.samlIdPCookieProps = "; Secure; SameSite=Lax"; // If set to a custom string, the string is appended to the cookie value
  this.setFocusTextBox = true; // Set to false to supress focus
  this.extraCompareRegex = null; // To ignore diacriticals say something like this.extraCompareRegex = new RegExp("\\p{Diacritic}", "gu")
  this.testGUI = false;

  this.autoFollowCookie = null; //  If you want auto-dispatch, set this to the cookie name to use
  this.autoFollowCookieTTLs = [1, 60, 270]; // Cookie life (in days).  Changing this requires changes to idp_select_languages
  this.autoFollowCookieProps = "; Secure; SameSite=Lax"; // If set to a custom string, the string is appended to the cookie value

  //
  // Language support.
  //
  // The minified source provides "en", "de", "pt-br" and "jp".
  //
  // Override any of these below, or provide your own language
  //
  //this.langBundles = {
  //'en': {
  //    'fatal.divMissing': '<div> specified  as "insertAtDiv" could not be located in the HTML',
  //    'fatal.noXMLHttpRequest': 'Browser does not support XMLHttpRequest, unable to load IdP selection data',
  //    'fatal.wrongProtocol' : 'Policy supplied to DS was not "urn:oasis:names:tc:SAML:profiles:SSO:idpdiscovery-protocol:single"',
  //    'fatal.wrongEntityId' : 'entityId supplied by SP did not match configuration',
  //    'fatal.noData' : 'Metadata download returned no data',
  //    'fatal.loadFailed': 'Failed to download metadata from ',
  //    'fatal.noparms' : 'No parameters to discovery session and no defaultReturn parameter configured',
  //    'fatal.noReturnURL' : "No URL return parameter provided",
  //    'fatal.badProtocol' : "Return request must start with https:// or http://",
  //    'idpPreferred.label': 'Use a suggested selection:',
  //    'idpEntry.label': 'Or enter your organization\'s name',
  //    'idpEntry.NoPreferred.label': 'Enter your organization\'s name',
  //    'idpList.label': 'Or select your organization from the list below',
  //    'idpList.NoPreferred.label': 'Select your organization from the list below',
  //    'idpList.defaultOptionLabel': 'Please select your organization...',
  //    'idpList.showList' : 'Allow me to pick from a list',
  //    'idpList.showSearch' : 'Allow me to specify the site',
  //    'submitButton.label': 'Continue',
  //    'helpText': 'Help',
  //    'defaultLogoAlt' : 'DefaultLogo'
  //}
  //};

  //
  // The following should not be changed without changes to the css.  Consider them as mandatory defaults
  //
  this.maxPreferredIdPs = 3;
  this.maxIdPCharsButton = 33;
  this.maxIdPCharsDropDown = 58;
  this.maxIdPCharsAltTxt = 60;

  this.minWidth = 20;
  this.minHeight = 20;
  this.maxWidth = 115;
  this.maxHeight = 69;
  this.bestRatio = Math.log(80 / 60);
}
