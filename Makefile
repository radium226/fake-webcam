SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -e -c
.ONESHELL:

SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -e -c
.ONESHELL:

VERSION = 0.1.0

include make/arch.mk

dist/fakewebcam-$(VERSION).tar.gz:
	poetry \
		build \
			--format="sdist" \
			--no-interaction

.PHONY: package
package: arch-package

.PHONY: clean
clean: arch-clean
	rm -Rf "dist"

.PHONY: install
install: arch-install