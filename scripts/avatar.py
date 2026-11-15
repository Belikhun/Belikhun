# Copyright (c) 2026 Belikhun. Licensed under the MIT License.
# See LICENSE at the repository root.

"""Pack the avatar's layers into one texture atlas for the rig.

The layered PSD comes from See-through (github.com/shitagaki-lab/see-through),
run on docs/assets/avatar-cutout.png. This needs psd-tools, so run it with the
Python of the See-through environment.
"""

import json
import os

import numpy
from PIL import Image
from psd_tools import PSDImage
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "docs", "assets", "avatar", "belikhun.psd")
ORIGINAL = os.path.join(ROOT, "docs", "assets", "avatar", "source.png")
ATLAS = os.path.join(ROOT, "static", "img", "avatar", "atlas.webp")
MANIFEST = os.path.join(ROOT, "src", "lib", "content", "avatar.json")

ATLAS_WIDTH = 2048
PADDING = 4
OPAQUE = 128

# How far from a boundary between parts the repaint starts, and how far it takes to reach full strength, in pixels.
MARGIN = 3
FEATHER = 5

# The layer behind everything else, and how unlike it a pixel of the original must be, and how
# close to another part, before that pixel is taken to belong to the other part.
BACKDROP = "back hair"
FOREIGN = 150
STRAY_REACH = 14

# The face's own layers barely move against each other, so they count as one part and are repainted right up to their edges.
FACE = {"face", "ears", "nose", "mouth", "eyebrow-l", "eyebrow-r", "eyewhite-l", "eyewhite-r", "irides-l", "irides-r", "eyelash-l", "eyelash-r"}
FACE_PART = 1000

# The face layers that sit on the skin.
FEATURES = FACE - {"face", "ears"}

# See-through orders layers by depth, which puts this eyebrow under the face.
RAISE_ABOVE = {"eyebrow-l": "face"}

# She wears no earrings; the model invented a pair and drew them on her cheek.
DROPPED = {"earwear"}


def stacking(names: list[str]) -> list[str]:
	"""The PSD's order, back to front, with the known mistakes corrected."""
	order = [name for name in names if name not in RAISE_ABOVE and name not in DROPPED]

	for name, below in RAISE_ABOVE.items():
		order.insert(order.index(below) + 1, name)

	return order


def reproject(psd: PSDImage, order: list[str]) -> dict[str, tuple[Image.Image, tuple[int, int, int, int]]]:
	"""Paint the original illustration back onto the layers.

	See-through redraws what it separates, so the eyes drift and small things
	(the hair ties) vanish. Every pixel of the original goes to the layer that
	is on top there; pixels no layer covers go to the nearest layer. The
	hidden, painted-in areas and a thin margin along each part's edge stay
	generated, and the resting pose matches the original closely.
	"""
	width, height = psd.size
	original = numpy.asarray(Image.open(ORIGINAL).convert("RGBA"))
	canvases = {}

	for layer in psd:
		canvas = numpy.zeros((height, width, 4), dtype=numpy.uint8)
		left, top, right, bottom = layer.bbox
		canvas[top:bottom, left:right] = numpy.asarray(layer.topil().convert("RGBA"))
		canvases[layer.name] = canvas

	# The generated eyes, brows and mouth are a little larger than the drawn
	# ones, and their soft edges show as a pale outline around each. Cut them
	# to their solid core; the original's own pixels carry the soft edge.
	for name in FEATURES:
		canvas = canvases[name]
		canvas[canvas[..., 3] < OPAQUE] = 0

	owner = numpy.full((height, width), -1, dtype=numpy.int32)
	part = numpy.full((height, width), -1, dtype=numpy.int32)

	for index, name in enumerate(order):
		solid = canvases[name][..., 3] >= OPAQUE
		owner[solid] = index
		part[solid] = FACE_PART if name in FACE else index

	# Near a boundary between two parts the original's pixels are a blend of
	# both, outline included. Painting them onto the layer behind would leave a
	# ghost outline there once the layers move apart, so the repaint fades out
	# towards every boundary and each layer keeps the outline it was given.
	boundary = numpy.zeros((height, width), dtype=bool)
	boundary[:, 1:] |= part[:, 1:] != part[:, :-1]
	boundary[:, :-1] |= part[:, 1:] != part[:, :-1]
	boundary[1:, :] |= part[1:, :] != part[:-1, :]
	boundary[:-1, :] |= part[1:, :] != part[:-1, :]
	trust = numpy.clip((ndimage.distance_transform_edt(~boundary) - MARGIN) / FEATHER, 0, 1)[..., None]

	nearest = ndimage.distance_transform_edt(owner < 0, return_distances=False, return_indices=True)
	claimed = owner[nearest[0], nearest[1]]
	drawn = original[..., 3] >= OPAQUE

	# Where a part reaches further in the original than its layer does, the
	# layer behind shows something that is not its own (a dress charm on the
	# hair). Such pixels go to the nearest part in front of it instead.
	behind = order.index(BACKDROP)
	backdrop = canvases[BACKDROP]
	foreign = numpy.abs(backdrop[..., :3].astype(int) - original[..., :3].astype(int)).sum(axis=2) > FOREIGN
	other = (owner >= 0) & (owner != behind)
	reach, closest = ndimage.distance_transform_edt(~other, return_indices=True)
	stray = (owner == behind) & drawn & foreign & (reach <= STRAY_REACH)
	adopter = owner[closest[0], closest[1]]

	for index, name in enumerate(order):
		adopted = stray & (adopter == index)
		canvases[name][adopted] = original[adopted]

	trust[stray] = 0
	pictures = {}

	for index, name in enumerate(order):
		canvas = canvases[name]
		visible = (owner == index) & drawn
		orphaned = (owner < 0) & (claimed == index) & drawn
		repainted = canvas * (1 - trust) + original * trust

		canvas[visible] = numpy.round(repainted[visible]).astype(numpy.uint8)
		canvas[orphaned] = original[orphaned]

		picture = Image.fromarray(canvas)
		box = picture.getbbox()

		# a feature too faint to survive the cut (the nose is three pixels) lives on in the face layer
		if box is None:
			continue

		pictures[name] = (picture.crop(box), box)

	return pictures


def build() -> None:
	"""Write the atlas and the manifest that places each layer in it."""
	psd = PSDImage.open(SOURCE)
	order = stacking([layer.name for layer in psd])
	pictures = reproject(psd, order)
	order = [name for name in order if name in pictures]

	# shelf packing, tallest first
	placed: dict[str, tuple[int, int]] = {}
	cursor_x = PADDING
	cursor_y = PADDING
	shelf = 0

	for name in sorted(order, key=lambda name: -pictures[name][0].height):
		picture = pictures[name][0]

		if cursor_x + picture.width + PADDING > ATLAS_WIDTH:
			cursor_x = PADDING
			cursor_y += shelf + PADDING
			shelf = 0

		placed[name] = (cursor_x, cursor_y)
		cursor_x += picture.width + PADDING
		shelf = max(shelf, picture.height)

	height = cursor_y + shelf + PADDING
	atlas = Image.new("RGBA", (ATLAS_WIDTH, height), (0, 0, 0, 0))
	layers = []

	for name in order:
		picture, box = pictures[name]
		left, top = placed[name]
		atlas.paste(picture, (left, top))
		layers.append({
			"name": name,
			"x": box[0],
			"y": box[1],
			"width": picture.width,
			"height": picture.height,
			"u": left,
			"v": top
		})

	os.makedirs(os.path.dirname(ATLAS), exist_ok=True)
	atlas.save(ATLAS, "WEBP", quality=92, method=6, exact=True)

	with open(MANIFEST, "w", encoding="utf-8", newline="\n") as manifest:
		json.dump({"size": list(psd.size), "atlas": [ATLAS_WIDTH, height], "layers": layers}, manifest, indent="\t")
		manifest.write("\n")

	print(f"{len(layers)} layers, atlas {ATLAS_WIDTH}x{height}, {os.path.getsize(ATLAS) // 1024} KB")


if __name__ == "__main__":
	build()
