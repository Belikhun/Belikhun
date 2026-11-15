# Copyright (c) 2026 Belikhun. Licensed under the MIT License.
# See LICENSE at the repository root.

"""
Draw the README's numbers: one band with the account's totals, and a card for
each of the most starred repositories, in the site's colours.

Runs on a schedule in GitHub Actions (.github/workflows/stats.yml), which
publishes the pictures on the `stats` branch so `main` gets no commits from
it. Needs nothing but Python: the font is lifted out of the banner.

Usage: python scripts/stats.py <output folder>
"""

import datetime
import html
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANNER = os.path.join(ROOT, ".github", "banner.svg")

USER = "Belikhun"
API = "https://api.github.com"
TOP = 5

WIDTH = 1200
INK = "#2a2440"
SOFT = "#6f6890"
PAGE = "#f7f5fc"
LINE = "#e2dcf1"
PINK = "#ecbcd6"
BLUE = "#a9d4ec"
LAV = "#b9a7d9"
PURPLE = "#8f7bd0"

STAR = "M50 0C54 34 66 46 100 50C66 54 54 66 50 100C46 66 34 54 0 50C34 46 46 34 50 0Z"
DESCRIPTION_LENGTH = 84

# How wide Bricolage Grotesque draws each character from space to ~, in thousandths of the
# font size, at the two weights used here. Measured in a browser, so the right side of every
# card can be laid out without one.
ADVANCES = {
	400: [254, 254, 296, 606, 624, 931, 757, 149, 296, 276, 375, 510, 149, 332, 177, 350, 651, 307, 573, 590, 580, 594, 641, 486, 640, 635, 189, 171, 510, 510, 510, 408, 935, 657, 657, 666, 686, 588, 570, 698, 701, 266, 349, 656, 508, 893, 733, 712, 621, 716, 650, 635, 544, 713, 649, 942, 630, 579, 554, 310, 334, 290, 534, 590, 283, 558, 607, 549, 606, 564, 370, 583, 596, 249, 259, 546, 248, 896, 596, 601, 607, 606, 399, 530, 371, 587, 534, 808, 516, 585, 488, 355, 254, 326, 510],
	800: [223, 303, 381, 633, 647, 992, 754, 187, 329, 329, 456, 534, 212, 359, 252, 365, 670, 360, 613, 611, 638, 615, 662, 517, 661, 658, 262, 237, 534, 534, 534, 425, 1004, 712, 692, 685, 705, 632, 601, 729, 730, 303, 382, 697, 509, 955, 790, 725, 654, 726, 688, 658, 579, 733, 682, 1001, 719, 662, 576, 329, 365, 329, 585, 543, 283, 595, 648, 571, 649, 587, 408, 607, 643, 286, 288, 605, 283, 963, 643, 612, 648, 649, 446, 549, 406, 634, 585, 881, 587, 608, 537, 347, 277, 347, 534],
}
UNKNOWN_ADVANCE = 650
DISPLAY_TRACKING = -0.03

EDGE = 36
STAR_SIZE = 24


def fetch(path):
	"""One answer from the GitHub API, signed in where the workflow gave a token."""
	request = urllib.request.Request(API + path, headers={"Accept": "application/vnd.github+json", "User-Agent": "readme-stats"})
	token = os.environ.get("GITHUB_TOKEN")

	if token:
		request.add_header("Authorization", f"Bearer {token}")

	with urllib.request.urlopen(request, timeout=30) as answer:
		return json.load(answer)


def commits(repos):
	"""Every commit of mine across the repositories, as their contributor lists count them."""
	total = 0

	for repo in repos:
		try:
			people = fetch(f"/repos/{USER}/{repo['name']}/contributors?per_page=100")
		except Exception:
			# an empty repository answers with no content
			continue

		if isinstance(people, list):
			total += sum(person["contributions"] for person in people if person.get("login") == USER)

	return total


def measure(text, size, weight):
	"""The width of a line of text in px; the display weight is set tighter, as `.display` sets it."""
	table = ADVANCES[weight]
	tracking = DISPLAY_TRACKING if weight == 800 else 0
	total = 0

	for char in text:
		code = ord(char) - 32
		total += (table[code] if 0 <= code < len(table) else UNKNOWN_ADVANCE) / 1000 + tracking

	return total * size


def styles(font):
	return (
		f"@font-face{{font-family:B;font-weight:200 800;src:url(data:font/woff2;base64,{font}) format('woff2')}}"
		f"text{{font-family:B,system-ui,sans-serif;fill:{INK}}}"
		".display{font-weight:800;letter-spacing:-.03em}"
		".up{animation:up .6s cubic-bezier(.16,1,.3,1) both}"
		".spin{animation:spin 6s linear infinite}"
		"@keyframes up{from{transform:translateY(20px);opacity:0}}"
		"@keyframes spin{to{transform:rotate(360deg)}}"
		"@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
	)


def star(x, y, size, colour):
	return (
		f'<g transform="translate({x} {y})"><g class="spin">'
		f'<path transform="scale({size / 100}) translate(-50 -50)" d="{STAR}" fill="{colour}"/>'
		f"</g></g>"
	)


def band(font, numbers, updated):
	"""The totals, on the same dark band as the hero's marquee."""
	height = 148
	column = WIDTH / len(numbers)
	cells = []

	for index, (label, value) in enumerate(numbers):
		x = column * index + column / 2

		cells.append(
			f'<g class="up" style="animation-delay:{0.2 + index * 0.08:.2f}s">'
			f'<text class="display" x="{x}" y="78" font-size="60" text-anchor="middle" style="fill:#fff">{value:,}</text>'
			f'<text x="{x}" y="108" font-size="16" text-anchor="middle" style="fill:{LAV}">{label}</text>'
			f"</g>"
		)

		if index:
			cells.append(star(column * index, 70, 26, PURPLE))

	return (
		f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="{html.escape(", ".join(f"{value} {label}" for label, value in numbers))}">'
		f"<style>{styles(font)}</style>"
		f'<rect width="{WIDTH}" height="{height}" rx="28" fill="{INK}"/>'
		f'{"".join(cells)}'
		f'<text x="{WIDTH - 28}" y="{height - 14}" font-size="11" text-anchor="end" style="fill:{SOFT}">updated {updated}</text>'
		f"</svg>\n"
	)


def card(font, rank, repo, column):
	"""One repository: its place, its name and what it is, its language and its stars."""
	height = 96
	first = rank == 1
	stars = f"{repo['stargazers_count']:,}"
	about = repo.get("description") or ""

	if len(about) > DESCRIPTION_LENGTH:
		about = about[: DESCRIPTION_LENGTH - 1].rstrip() + "…"

	# the star sits left of the widest count among the cards, so stars and pills line up down the list
	mark = WIDTH - EDGE - column - 12 - STAR_SIZE / 2
	language = repo.get("language")
	pill = ""

	if language:
		width = round(measure(language, 14, 400)) + 28
		right = mark - STAR_SIZE / 2 - 20

		pill = (
			f'<rect x="{right - width}" y="34" width="{width}" height="28" rx="14" fill="{PINK if rank % 2 else BLUE}"/>'
			f'<text x="{right - width / 2}" y="53" font-size="14" text-anchor="middle">{html.escape(language)}</text>'
		)

	ground = (
		'<linearGradient id="sky" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a9d4ec"/><stop offset=".58" stop-color="#b9a7d9"/><stop offset="1" stop-color="#ecbcd6"/></linearGradient>'
		f'<rect width="{WIDTH}" height="{height}" rx="24" fill="url(#sky)"/>'
		if first
		else f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1}" rx="24" fill="{PAGE}" stroke="{LINE}"/>'
	)
	number = (
		f'<text class="display" x="36" y="63" font-size="44" style="fill:#fff">{rank:02}</text>'
		if first
		else f'<text class="display" x="36" y="63" font-size="44" stroke="{PURPLE}" stroke-width="2" stroke-linejoin="round" paint-order="stroke" style="fill:{PAGE}">{rank:02}</text>'
	)

	return (
		f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="{html.escape(repo["name"])}: {stars} stars">'
		f"<style>{styles(font)}</style>"
		f"{ground}"
		f'<g class="up" style="animation-delay:{0.1 + rank * 0.08:.2f}s">'
		f"{number}"
		f'<text class="display" x="124" y="{46 if about else 58}" font-size="28" style="letter-spacing:-.02em">{html.escape(repo["name"])}</text>'
		f'<text x="124" y="71" font-size="15" style="fill:{INK if first else SOFT}">{html.escape(about)}</text>'
		f"{pill}"
		f'{star(mark, 48, STAR_SIZE, "#fff" if first else PURPLE)}'
		f'<text class="display" x="{WIDTH - EDGE}" y="59" font-size="30" text-anchor="end">{stars}</text>'
		f"</g>"
		f"</svg>\n"
	)


def main():
	target = sys.argv[1]

	with open(BANNER, encoding="utf-8") as file:
		font = re.search(r"base64,([A-Za-z0-9+/=]+)\) format\('woff2'\)", file.read()).group(1)

	user = fetch(f"/users/{USER}")
	repos = fetch(f"/search/repositories?q=user:{USER}&per_page=100")["items"]
	ranked = sorted(repos, key=lambda repo: repo["stargazers_count"], reverse=True)[:TOP]
	now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))

	numbers = [
		("stars", sum(repo["stargazers_count"] for repo in repos)),
		("repositories", len(repos)),
		("followers", user["followers"]),
		("commits", commits(repos)),
	]

	os.makedirs(target, exist_ok=True)

	pictures = {"stats.svg": band(font, numbers, now.strftime("%d/%m/%Y %H:%M (GMT+7)"))}

	column = max(measure(f"{repo['stargazers_count']:,}", 30, 800) for repo in ranked)

	for index, repo in enumerate(ranked):
		pictures[f"top-{index + 1}.svg"] = card(font, index + 1, repo, column)

	for name, picture in pictures.items():
		with open(os.path.join(target, name), "w", encoding="utf-8", newline="\n") as file:
			file.write(picture)

	print(", ".join(f"{value} {label}" for label, value in numbers))
	print("top:", ", ".join(repo["name"] for repo in ranked))


if __name__ == "__main__":
	main()
