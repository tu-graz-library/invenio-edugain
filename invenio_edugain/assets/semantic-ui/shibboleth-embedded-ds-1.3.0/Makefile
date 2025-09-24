# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Changes by Graz University of Technology:
#   - add legal header

#
# Note: Changes made here should be reflected in the windows .bat file at src/build.bat
#
INSTALL=/usr/bin/install
JAVA=java
TAR=tar
ZIP=zip
TARGET=shibboleth-embedded-ds-1.3.0
prefix=
sysconfdir=${prefix}/etc

all:

install:	index.html
	${INSTALL} -d $(DESTDIR)${sysconfdir}/shibboleth-ds
	${INSTALL} -m 644 *.txt *.html *.css *.gif *.js *.conf $(DESTDIR)${sysconfdir}/shibboleth-ds

clean:
	rm -rf ${TARGET}

kit:	clean
	mkdir ${TARGET}
	mkdir ${TARGET}/nonminimised
	cat src/javascript/idpselect_languages.js src/javascript/typeahead.js src/javascript/idpselect.js | ${JAVA} -jar build/yuicompressor-2.4.8.jar -o ${TARGET}/idpselect.js --type js
	cp Makefile shibboleth-embedded-ds.spec LICENSE.txt doc/*.txt src/resources/index.html src/resources/idpselect.css src/resources/blank.gif src/javascript/idpselect_config.js src/apache/*.conf ${TARGET}
	cp src/javascript/*.js ${TARGET}/nonminimised

dist:	kit
	${TAR} czf ${TARGET}.tar.gz ${TARGET}/*
	${ZIP} ${TARGET}.zip ${TARGET}/*
	rm -rf ${TARGET}
