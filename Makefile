SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -e -c
.ONESHELL:

FAKE_CAMERA_LABEL = Fake Webcam
# FIXME: Should be infered by label
FAKE_CAMERA_DEVICE = /dev/video2

SAMPLE_IMAGE_FILE = space.jpg

FAKE_CAMERA_WIDTH = 800
FAKE_CAMERA_HEIGHT = 600

.PHONY: create-camera
create-camera:
	sudo modprobe v4l2loopback \
		devices=1 \
		card_label="$(FAKE_CAMERA_LABEL)" \
		exclusive_caps=1

.PHONY: clean
clean:
	sudo modprobe --remove v4l2loopback

.PHONY: list-cameras
list-cameras:
	v4l2-ctl --list-devices

.PHONY: fake-camera
fake-camera:
	ffmpeg \
		-re \
		-loop "1" \
		-i "$(SAMPLE_IMAGE_FILE)" \
		-vf "scale=iw*min($(FAKE_CAMERA_WIDTH)/iw\,$(FAKE_CAMERA_HEIGHT)/ih):ih*min($(FAKE_CAMERA_WIDTH)/iw\,$(FAKE_CAMERA_HEIGHT)/ih),pad=$(FAKE_CAMERA_WIDTH):$(FAKE_CAMERA_HEIGHT):($(FAKE_CAMERA_WIDTH)-iw)/2:($(FAKE_CAMERA_HEIGHT)-ih)/2" \
		-vcodec "rawvideo" \
		-pix_fmt "yuv420p" \
		-f "v4l2" \
		"$(FAKE_CAMERA_DEVICE)"