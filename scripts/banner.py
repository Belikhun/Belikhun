# Copyright (c) 2026 Belikhun. Licensed under the MIT License.
# See LICENSE at the repository root.

"""
Draw the README's banner: the site's hero as one animated SVG.

GitHub shows the banner through an <img>, where no script runs and nothing
outside the file is fetched. So the font and the avatar's layers are embedded,
every motion is a CSS animation, and the avatar's rig (src/lib/avatar/rig.ts)
is redrawn with what CSS can do: each layer moves as a whole, and the two that
bend, the back hair and the dress, are cut into pieces that each sway a little
later than the one before.
"""

import base64
import datetime
import io
import json
import math
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATLAS = os.path.join(ROOT, "static", "img", "avatar", "atlas.webp")
MANIFEST = os.path.join(ROOT, "src", "lib", "content", "avatar.json")
FONT = os.path.join(ROOT, "node_modules", "@fontsource-variable", "bricolage-grotesque", "files", "bricolage-grotesque-latin-wght-normal.woff2")
TARGET = os.path.join(ROOT, ".github", "banner.svg")

WIDTH = 1200
HEIGHT = 662
FRAME = 12
CARD = {"x": FRAME, "y": FRAME, "width": WIDTH - FRAME * 2, "height": 548, "radius": 32}
BAND = {"y": CARD["y"] + CARD["height"] + FRAME, "height": 90}

INK = "#2a2440"
PAGE = "#f7f5fc"
TONES = {"pink": "#ecbcd6", "blue": "#a9d4ec", "purple": "#8f7bd0", "lav": "#b9a7d9"}

# Bricolage Grotesque at weight 800, measured in a browser, in thousandths of the font size
WORDMARK = "belikhun"
WORDMARK_STARTS = [0, 648, 1235, 1518, 1804, 2409, 3052, 3686]
WORDMARK_WIDTH = 4329
PHRASES = [("fullstack web engineer", 11284, "💻", "pink", -6), ("builds free software with", 12474, "❤️", "blue", 6)]
TRACKING = -0.03
ASCENT = 0.93
DESCENT = 0.27

# the same shards as Hero.svelte: where in the card, how wide in px, how far turned
SHARDS = [
	(12, 30, 40, 24, "pink"),
	(22, 66, 24, -18, "blue"),
	(31, 72, 20, 40, "purple"),
	(70, 70, 32, -30, "blue"),
	(79, 58, 48, 14, "pink"),
	(88, 28, 24, 60, "purple"),
	(60, 78, 20, -50, "blue"),
]

# the rig's own numbers, in the model's pixels
SOURCE_BOX = {"x": 262.5, "y": 0, "width": 755, "height": 1280}
HEAD = (540, 190)
NECK = (552, 300)
SHOULDERS = {"handwear-r": (490, 330, 1), "handwear-l": (631, 330, -1)}
HIP = (705, 655)
WAIST = 470
HEM = 1073
EYES = {"r": (207, 250), "l": (184, 229)}

# how much of its size a layer keeps when it is embedded: enough for a banner shown at twice its width
LAYER_SCALE = 0.6
LAYER_QUALITY = 84

RING = 45
STRIP = 45
OVERLAP = 3

# the year of the timeline's first stop; the chip counts from it
SINCE = 2017

# seconds before anything moves, so the banner is on screen before it starts
START = 0.4


def smooth(start, end, value):
	amount = min(1, max(0, (value - start) / (end - start)))

	return amount * amount * (3 - 2 * amount)


def number(value):
	return f"{value:.2f}".rstrip("0").rstrip(".")


def pivot(point, name, inner, style=""):
	"""Wraps `inner` so the animation `name` turns and scales about `point`."""
	x, y = number(point[0]), number(point[1])
	style = f' style="{style}"' if style else ""

	return f'<g transform="translate({x} {y})"><g class="{name}"{style}><g transform="translate(-{x} -{y})">{inner}</g></g></g>'


def embed(picture):
	"""A layer as a data URI, scaled down for the banner."""
	size = (max(1, round(picture.width * LAYER_SCALE)), max(1, round(picture.height * LAYER_SCALE)))
	buffer = io.BytesIO()

	picture.resize(size, Image.LANCZOS).save(buffer, "WEBP", quality=LAYER_QUALITY, method=6)

	return "data:image/webp;base64," + base64.b64encode(buffer.getvalue()).decode()


def layer_image(layer, atlas, identity=""):
	box = (layer["u"], layer["v"], layer["u"] + layer["width"], layer["v"] + layer["height"])
	identity = f' id="{identity}"' if identity else ""

	return f'<image{identity} x="{layer["x"]}" y="{layer["y"]}" width="{layer["width"]}" height="{layer["height"]}" href="{embed(atlas.crop(box))}"/>'


def swaying(piece, sway, wave, phase, period):
	"""A piece that leans with the gust and carries a wave that reaches it `phase` seconds late."""
	if sway < 0.05 and wave < 0.05:
		return piece

	delay = number(phase - period * 4)

	return f'<g class="gust" style="--a:{number(sway)}px"><g class="wave" style="--b:{number(wave)}px;animation-duration:{number(period / 2)}s;animation-delay:{delay}s">{piece}</g></g>'


def back_hair(layer, atlas, defs):
	"""The back hair in rings around the head: the roots follow the head, the lengths lag behind and swing."""
	defs.append(layer_image(layer, atlas, "back-hair"))

	reach = max(
		math.hypot(x - HEAD[0], y - HEAD[1])
		for x in (layer["x"], layer["x"] + layer["width"])
		for y in (layer["y"], layer["y"] + layer["height"])
	)
	edges = [0, 120]

	while edges[-1] < reach:
		edges.append(edges[-1] + RING)

	pieces = []

	for index in range(len(edges) - 1):
		inner, outer = edges[index], edges[index + 1] + OVERLAP
		distance = (edges[index] + edges[index + 1]) / 2
		loose = smooth(120, 640, distance)
		follow = 1 - smooth(110, 420, distance)
		hole = (
			f"M{HEAD[0] - inner} {HEAD[1]}a{inner} {inner} 0 1 0 {inner * 2} 0a{inner} {inner} 0 1 0 -{inner * 2} 0Z"
			if inner
			else ""
		)

		defs.append(
			f'<clipPath id="ring-{index}"><path clip-rule="evenodd" d="M{HEAD[0] - outer} {HEAD[1]}a{outer} {outer} 0 1 0 {outer * 2} 0a{outer} {outer} 0 1 0 -{outer * 2} 0Z{hole}"/></clipPath>'
		)

		piece = f'<use href="#back-hair" clip-path="url(#ring-{index})"/>'
		piece = swaying(piece, 0.14 * loose * loose * 70, loose * 7, distance * 0.011 / 1.6, math.tau / 1.6)

		if follow > 0.02:
			piece = pivot(NECK, "turn", piece, f"--w:{number(follow)}")

		pieces.append(piece)

	return "".join(pieces)


def dress(layer, atlas, defs):
	"""The dress in strips: still at the waist, swaying more towards the hem."""
	defs.append(layer_image(layer, atlas, "dress"))

	edges = [layer["y"], WAIST]

	while edges[-1] < layer["y"] + layer["height"]:
		edges.append(edges[-1] + STRIP)

	pieces = []

	for index in range(len(edges) - 1):
		top, bottom = edges[index], edges[index + 1] + OVERLAP
		middle = (edges[index] + edges[index + 1]) / 2
		below = smooth(WAIST, HEM, middle)

		defs.append(f'<clipPath id="strip-{index}"><rect x="{layer["x"] - 80}" y="{top}" width="{layer["width"] + 160}" height="{bottom - top}"/></clipPath>')

		piece = f'<use href="#dress" clip-path="url(#strip-{index})"/>'
		pieces.append(swaying(piece, 0.1 * below * below * 45, below * 5, middle * 0.012 / 1.4, math.tau / 1.4))

	return "".join(pieces)


def eye(name, layer, atlas):
	"""An eye's layer closes towards its lower lid; the lashes come down to meet it."""
	top, bottom = EYES[name[-1]]
	picture = layer_image(layer, atlas)

	if name.startswith("eyelash"):
		return f'<g class="lash" style="--d:{number((bottom - top) * 0.62)}px">{picture}</g>'

	if name.startswith("irides"):
		picture = f'<g class="look">{picture}</g>'

	return pivot((0, bottom), "lid", picture)


def avatar(defs):
	"""The avatar's layers, bottom to top, each inside the motions it takes part in."""
	atlas = Image.open(ATLAS).convert("RGBA")

	with open(MANIFEST, encoding="utf-8") as file:
		layers = json.load(file)["layers"]

	def upper(inner):
		# the whole upper body leans a little with the head and lifts with the breath
		return pivot(HIP, "lean", f'<g class="breath">{inner}</g>')

	parts = []
	head = []

	for layer in layers:
		name = layer["name"]

		if name == "back hair":
			parts.append(upper(back_hair(layer, atlas, defs)))
		elif name in ("footwear", "legwear"):
			parts.append(pivot(HIP, "legs", layer_image(layer, atlas)))
		elif name in SHOULDERS:
			x, y, side = SHOULDERS[name]
			parts.append(upper(pivot((x, y), "arm", layer_image(layer, atlas), f"--side:{side}")))
		elif name == "topwear":
			parts.append(upper(dress(layer, atlas, defs)))
		elif name == "neck":
			parts.append(upper(layer_image(layer, atlas)))
		elif name[:7] in ("eyewhit", "irides-", "eyelash"):
			head.append(eye(name, layer, atlas))
		else:
			head.append(layer_image(layer, atlas))

	parts.append(upper(pivot(NECK, "turn", f'<g class="nod">{"".join(head)}</g>', "--w:1")))

	return "".join(parts)


def blink_frames():
	"""Three blinks in an eleven second loop, the last two close together."""
	loop = 11
	frames = []

	for at in (2.6, 6.9, 7.15):
		frames.append((at, 1))
		frames.append((at + 0.07, 0))
		frames.append((at + 0.2, 1))

	lid = "".join(f"{number(at / loop * 100)}%{{transform:scaleY({max(open_, 0.04)})}}" for at, open_ in frames)
	lash = "".join(f"{number(at / loop * 100)}%{{transform:translateY(calc(var(--d)*{1 - open_}))}}" for at, open_ in frames)

	return f"@keyframes lid{{{lid}}}@keyframes lash{{{lash}}}"


def styles(font):
	sine = "cubic-bezier(.37,0,.63,1)"
	quart = "cubic-bezier(.17,.84,.44,1)"
	cubic = "cubic-bezier(.22,.61,.36,1)"
	back = "cubic-bezier(.34,1.7,.64,1)"

	return f"""
@font-face{{font-family:B;font-weight:200 800;src:url(data:font/woff2;base64,{font}) format('woff2')}}
text{{font-family:B,system-ui,sans-serif;fill:{INK}}}
.display{{font-weight:800;letter-spacing:{TRACKING}em}}
.emoji{{font-family:'Segoe UI Emoji','Apple Color Emoji','Noto Color Emoji',sans-serif;letter-spacing:0}}

.char{{animation:rise .9s {quart} both}}
.arrive{{animation:arrive 1.2s {cubic} {number(START + 0.25)}s both}}
.band{{animation:lift .7s {cubic} {number(START + 0.4)}s both}}
.pop{{animation:pop .6s {back} both}}
.chip{{animation:chip .5s ease-out both}}
@keyframes rise{{from{{transform:translateY(261px)}}}}
@keyframes arrive{{from{{transform:translateY(60px) scale(.92);opacity:0}}}}
@keyframes lift{{from{{transform:translateY({BAND["height"]}px)}}}}
@keyframes pop{{from{{transform:scale(0);opacity:0}}}}
@keyframes chip{{from{{transform:translateY(16px);opacity:0}}}}

.float{{animation:float 3.2s {sine} infinite alternate}}
.bob{{animation:bob 2.4s {sine} infinite alternate}}
.track{{animation:run 14s linear infinite}}
.star{{animation:spin 6s linear infinite}}
@keyframes float{{to{{transform:translateY(-16px)}}}}
@keyframes bob{{to{{transform:translateY(var(--y)) rotate(var(--r))}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}

.lean{{animation:lean 7s {sine} infinite alternate}}
.turn{{animation:turn 7s {sine} infinite alternate}}
.nod{{animation:nod 10s {sine} infinite alternate}}
.look{{animation:look 7s {sine} infinite alternate}}
.breath{{animation:breath 2.3s {sine} infinite alternate}}
.arm{{animation:arm 2.3s {sine} infinite alternate}}
.legs{{animation:legs 3.5s {sine} infinite alternate}}
.gust{{animation:gust 4.5s {sine} infinite alternate}}
.wave{{animation:wave 2s {sine} infinite alternate}}
.lid{{animation:lid 11s linear infinite}}
.lash{{animation:lash 11s linear infinite}}
@keyframes lean{{from{{transform:rotate(-.7deg)}}to{{transform:rotate(.7deg)}}}}
@keyframes turn{{from{{transform:translateX(calc(var(--w)*-4px)) rotate(calc(var(--w)*-2deg))}}to{{transform:translateX(calc(var(--w)*4px)) rotate(calc(var(--w)*2deg))}}}}
@keyframes nod{{from{{transform:translateY(-2px)}}to{{transform:translateY(2px)}}}}
@keyframes look{{from{{transform:translateX(-2.2px)}}to{{transform:translateX(2.2px)}}}}
@keyframes breath{{to{{transform:translateY(-3px)}}}}
@keyframes arm{{to{{transform:rotate(calc(var(--side)*.8deg))}}}}
@keyframes legs{{from{{transform:rotate(-.57deg)}}to{{transform:rotate(.57deg)}}}}
@keyframes gust{{from{{transform:translateX(calc(var(--a)*-1))}}to{{transform:translateX(var(--a))}}}}
@keyframes wave{{from{{transform:translateX(calc(var(--b)*-1))}}to{{transform:translateX(var(--b))}}}}
{blink_frames()}

@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""


def wordmark():
	size = 252
	top = CARD["y"] + CARD["height"] * 0.11
	line = size * 0.9
	baseline = top + (0.9 - ASCENT - DESCENT) / 2 * size + ASCENT * size
	width = (WORDMARK_WIDTH / 1000 + TRACKING * len(WORDMARK)) * size
	left = WIDTH / 2 - width / 2
	chars = []

	for index, char in enumerate(WORDMARK):
		x = left + (WORDMARK_STARTS[index] / 1000 + TRACKING * index) * size
		delay = number(START + index * 0.045)

		chars.append(f'<text class="display char" style="fill:#fff;animation-delay:{delay}s" x="{number(x)}" y="{number(baseline)}" font-size="{size}">{char}</text>')

	clip = f'<clipPath id="line"><rect x="0" y="{number(top)}" width="{WIDTH}" height="{number(line)}"/></clipPath>'

	return clip, f'<g clip-path="url(#line)">{"".join(chars)}</g>'


def shards():
	out = []

	for index, (left, top, width, turn, tone) in enumerate(SHARDS):
		height = width * 5 / 3
		x = CARD["x"] + CARD["width"] * left / 100 + width / 2
		y = CARD["y"] + CARD["height"] * top / 100 + height / 2
		points = " ".join(
			f"{number(px * width - width / 2)},{number(py * height - height / 2)}"
			for px, py in ((0.3, 0), (1, 0.18), (0.7, 1), (0, 0.82))
		)
		drift = -12 if index % 2 == 0 else 12
		sway = 8 if index % 2 == 0 else -8

		out.append(
			f'<g transform="translate({number(x)} {number(y)})">'
			f'<g class="pop" style="animation-delay:{number(START + 0.5 + index * 0.05)}s">'
			f'<g class="bob" style="--y:{drift}px;--r:{sway}deg;animation-duration:{number(2.4 + index * 0.35)}s">'
			f'<polygon transform="rotate({turn})" points="{points}" fill="{TONES[tone]}"/>'
			f"</g></g></g>"
		)

	return "".join(out)


def chips():
	bottom = CARD["y"] + CARD["height"]
	left = CARD["x"]
	right = CARD["x"] + CARD["width"]

	years = (
		f'<g class="chip" style="animation-delay:{number(START + 0.7)}s">'
		f'<path d="M{left} {bottom - 80}h160a24 24 0 0 1 24 24v56h-184z" fill="{PAGE}"/>'
		f'<text class="display" x="{left + 24}" y="{bottom - 39}" font-size="32" style="letter-spacing:-.02em">{datetime.date.today().year - SINCE} yrs</text>'
		f'<text x="{left + 24}" y="{bottom - 21}" font-size="14">of building things <tspan class="emoji">🚀</tspan></text>'
		f"</g>"
	)
	site = (
		f'<g class="chip" style="animation-delay:{number(START + 0.8)}s">'
		f'<path d="M{right} {bottom - 50}h-128a24 24 0 0 0 -24 24v26h152z" fill="{PAGE}"/>'
		f'<text x="{right - 24}" y="{bottom - 20}" font-size="14" text-anchor="end">belikhun.dev  ↗</text>'
		f"</g>"
	)

	return years + site


def marquee():
	size = 55
	gap = 24
	middle = BAND["y"] + BAND["height"] / 2
	baseline = middle + (ASCENT - DESCENT) / 2 * size
	star = 29
	badge = {"width": 78, "height": 44}
	copy = []
	x = 0

	for index, (text, width, emoji, tone, turn) in enumerate(PHRASES):
		outlined = (
			f' fill="{INK}" stroke="{TONES["lav"]}" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke"'
			if index % 2 == 1
			else ' fill="#fff"'
		)

		copy.append(f'<text class="display" x="{number(x)}" y="{number(baseline)}" font-size="{size}"{outlined} style="fill:{INK if index % 2 == 1 else "#fff"}">{text}</text>')
		x += (width / 1000 + TRACKING * len(text)) * size + gap

		copy.append(
			f'<g transform="translate({number(x + badge["width"] / 2)} {number(middle)}) rotate({turn})">'
			f'<rect x="{-badge["width"] / 2}" y="{-badge["height"] / 2}" width="{badge["width"]}" height="{badge["height"]}" rx="{badge["height"] / 2}" fill="{TONES[tone]}"/>'
			f'<text class="emoji" y="12" font-size="34" text-anchor="middle">{emoji}</text>'
			f"</g>"
		)
		x += badge["width"] + gap

		copy.append(
			f'<g transform="translate({number(x + star / 2)} {number(middle)})"><g class="star">'
			f'<path transform="scale({star / 100}) translate(-50 -50)" d="M50 0C54 34 66 46 100 50C66 54 54 66 50 100C46 66 34 54 0 50C34 46 46 34 50 0Z" fill="{TONES["lav"]}"/>'
			f"</g></g>"
		)
		x += star + gap

	copies = math.ceil(WIDTH / x) + 1
	track = "".join(f'<g transform="translate({number(x * index)} 0)">{"".join(copy)}</g>' for index in range(copies))
	run = f"@keyframes run{{to{{transform:translateX(-{number(x)}px)}}}}"

	return run, (
		f'<g class="band">'
		f'<rect x="0" y="{BAND["y"]}" width="{WIDTH}" height="{BAND["height"]}" fill="{INK}"/>'
		f'<g class="track">{track}</g>'
		f"</g>"
	)


def sky():
	"""The card's gradient, 165 degrees as CSS counts them."""
	angle = math.radians(165)
	across, down = math.sin(angle), -math.cos(angle)
	half = (abs(CARD["width"] * across) + abs(CARD["height"] * down)) / 2
	x = CARD["x"] + CARD["width"] / 2
	y = CARD["y"] + CARD["height"] / 2

	return (
		f'<linearGradient id="sky" gradientUnits="userSpaceOnUse" x1="{number(x - across * half)}" y1="{number(y - down * half)}" x2="{number(x + across * half)}" y2="{number(y + down * half)}">'
		f'<stop offset="0" stop-color="#a9d4ec"/><stop offset=".58" stop-color="#b9a7d9"/><stop offset="1" stop-color="#ecbcd6"/>'
		f"</linearGradient>"
	)


def main():
	with open(FONT, "rb") as file:
		font = base64.b64encode(file.read()).decode()

	defs = [sky()]
	line, name = wordmark()
	run, band = marquee()

	defs.append(line)
	defs.append(f'<clipPath id="frame"><rect width="{WIDTH}" height="{HEIGHT}" rx="28"/></clipPath>')
	defs.append(f'<clipPath id="card"><rect x="{CARD["x"]}" y="{CARD["y"]}" width="{CARD["width"]}" height="{CARD["height"]}" rx="{CARD["radius"]}"/></clipPath>')

	# the avatar's box in the card, as Hero.svelte places it: 92% of the card's height, a little below its bottom edge
	tall = CARD["height"] * 0.92
	scale = tall / SOURCE_BOX["height"]
	top = CARD["y"] + CARD["height"] * 1.04 - tall
	left = WIDTH / 2 - SOURCE_BOX["width"] * scale / 2 - SOURCE_BOX["x"] * scale
	figure = f'<g class="float"><g transform="translate({number(left)} {number(top)}) scale({scale:.4f})">{avatar(defs)}</g></g>'

	svg = (
		f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="belikhun: fullstack web engineer, builds free software with love">'
		f"<style>{styles(font)}{run}</style>"
		f'<defs>{"".join(defs)}</defs>'
		f'<g clip-path="url(#frame)">'
		f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{PAGE}"/>'
		f'<g clip-path="url(#card)">'
		f'<rect x="{CARD["x"]}" y="{CARD["y"]}" width="{CARD["width"]}" height="{CARD["height"]}" fill="url(#sky)"/>'
		f"{name}{shards()}"
		f'{pivot((WIDTH / 2, top + tall / 2), "arrive", figure)}'
		f"{chips()}"
		f"</g>"
		f"{band}"
		f"</g></svg>\n"
	)

	os.makedirs(os.path.dirname(TARGET), exist_ok=True)

	with open(TARGET, "w", encoding="utf-8", newline="\n") as file:
		file.write(svg)

	print(f"wrote {os.path.relpath(TARGET, ROOT)}: {len(svg) / 1024:.0f} KB")


if __name__ == "__main__":
	main()
