packages/arch/fakewebcam-$(VERSION).tar.gz: dist/fakewebcam-$(VERSION).tar.gz
	cp "dist/fakewebcam-$(VERSION).tar.gz" "packages/arch/fakewebcam-$(VERSION).tar.gz"


packages/arch/fake-webcam-$(VERSION)-1-any.pkg.tar.xz: packages/arch/fakewebcam-$(VERSION).tar.gz
	cd "packages/arch"
	makepkg \
		--syncdeps \
		--cleanbuild \
		--clean \
		--noconfirm \
		--force

.PHONY: arch-package
arch-package: packages/arch/fake-webcam-$(VERSION)-1-any.pkg.tar.xz


.PHONY: arch-install
arch-install: arch-package
	yay -U 'packages/arch/fake-webcam-$(VERSION)-1-any.pkg.tar.xz' --noconfirm

.PHONY: arch-clean
arch-clean:
	find "packages/arch" -name "*.tar.gz" -o -name "*.pkg.tar.xz" -print | xargs -I {} echo rm -f "{}"
	
