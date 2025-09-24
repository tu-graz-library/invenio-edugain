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
