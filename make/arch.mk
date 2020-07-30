packages/arch/fakewebcam-$(VERSION).tar.gz: dist/fakewebcam-$(VERSION).tar.gz
	cp "dist/fakewebcam-$(VERSION).tar.gz" "packages/arch/fakewebcam-$(VERSION).tar.gz"


packages/arch/fake-webcam-$(VERSION)-1-any.pkg.tar.zst: packages/arch/fakewebcam-$(VERSION).tar.gz
	cd "packages/arch"
	PACMAN=yay \
		makepkg \
			--syncdeps \
			--cleanbuild \
			--clean \
			--noconfirm \
			--force

.PHONY: arch-package
arch-package: packages/arch/fake-webcam-$(VERSION)-1-any.pkg.tar.zst


.PHONY: arch-install
arch-install: arch-package
	yay -U 'packages/arch/fake-webcam-$(VERSION)-1-any.pkg.tar.zst' --noconfirm

.PHONY: arch-clean
arch-clean:
	find "packages/arch" \( -name "*.tar.gz" -o -name "*.pkg.tar.zst" \) -print | xargs -I {} rm -f "{}"
	
