# Copyright (c) 2026 Belikhun. All rights reserved.
# Proprietary software: use, copying, modification and distribution are
# prohibited without written permission. See LICENSE at the repository root.

"""Resize the source pictures under docs/assets into static/img and record their sizes."""

import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "docs", "assets")
TARGET = os.path.join(ROOT, "static", "img")
MANIFEST = os.path.join(ROOT, "src", "lib", "content", "media.json")

# target path: (source path, width, quality)
PICTURES = {
	"avatar.webp": ("avatar-cutout.png", 708, 92),
	"luna/icon.webp": ("luna/icon-borderless.png", 256, 90),
	"luna/wall/instances.webp": ("luna/console/instances.webp", 900, 80),
	"luna/wall/machine-health.webp": ("luna/console/machine-health.webp", 900, 80),
	"luna/wall/monitoring.webp": ("luna/console/monitoring.webp", 900, 80),
	"luna/wall/instance-console.webp": ("luna/console/instance-console.webp", 900, 80),
	"luna/wall/terminal.webp": ("luna/console/terminal.webp", 900, 80),
	"luna/wall/plugins.webp": ("luna/console/plugins.webp", 900, 80),
	"luna/wall/machines.webp": ("luna/console/machines.webp", 900, 80),
	"luna/wall/proxy.webp": ("luna/console/proxy.webp", 900, 80),
	"luna/wall/world.webp": ("luna/console/world.webp", 900, 80),
	"luna/wall/boat-racing.webp": ("luna/banner (0-00-00-45).png", 900, 82),
	"luna/wall/console-banner.webp": ("luna/console.png", 900, 86),
	"luna/wall/create-banner.webp": ("luna/luna-create-banner-1593.png", 900, 86),
	"luna/wall/lantern.webp": ("luna/game/lantern.webp", 900, 82),
	"harbor/meo-beo.webp": ("harbor/meo-beo.webp", 512, 90),
	"themis/light.webp": ("themis/light.png", 1400, 82),
	"themis/dark.webp": ("themis/dark.png", 1400, 82),
	"themis/overview.webp": ("themis/allin1.png", 1305, 84),
	"ctms/schedule.webp": ("ctms/screenshot0.png", 1200, 84),
	"ctms/phone-schedule.webp": ("ctms/screenshot1.png", 500, 84),
	"ctms/phone-register.webp": ("ctms/screenshot2.png", 500, 84),
	"rows/deal-hunter-suite.webp": ("rows/deal-hunter-splash.png", 402, 86)
}


def build() -> None:
	"""Write every picture and the size manifest."""
	sizes: dict[str, list[int]] = {}

	for target, (source, width, quality) in PICTURES.items():
		picture = Image.open(os.path.join(SOURCE, source))
		picture = picture.convert("RGBA" if picture.mode in ("RGBA", "LA", "P") else "RGB")

		if picture.width > width:
			height = round(picture.height * width / picture.width)
			picture = picture.resize((width, height), Image.LANCZOS)

		path = os.path.join(TARGET, target)
		os.makedirs(os.path.dirname(path), exist_ok=True)
		picture.save(path, "WEBP", quality=quality, method=6)
		sizes[target] = [picture.width, picture.height]

	with open(MANIFEST, "w", encoding="utf-8", newline="\n") as manifest:
		json.dump(sizes, manifest, indent="\t")
		manifest.write("\n")

	print(f"{len(sizes)} pictures")


if __name__ == "__main__":
	build()
