#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib import ehook;
from lib.log import log;

import colorama
from colorama import Fore
colorama.init()
log("OKAY", "Imported: colorama")

from datetime import datetime
log("OKAY", "Imported: datetime.datetime")

from time import perf_counter
log("OKAY", "Imported: time.perf_counter")

import requests
log("OKAY", "Imported: requests")

import json
log("OKAY", "Imported: json")

def logStatus(text, status, overWrite = False):
	statusText = [f"{Fore.RED}✗ ERRR", f"{Fore.YELLOW}● WAIT", f"{Fore.GREEN}✓ OKAY"]
	logStatus = ["ERRR", "INFO", "OKAY"]

	log(logStatus[status + 1], "{:48}{}{}".format(text, statusText[status + 1], Fore.RESET), resetCursor = (not overWrite))

##? ============= FETCH DATA =============
logStatus("Fetching User Data", 0)
USER_DATA = None

try:
	USER_DATA = requests.get("https://api.github.com/users/belivipro9x99").json()
except json.JSONDecodeError as error:
	logStatus("Parse User Data Failed: Malformed JSON Data", -1, True)
	raise error

logStatus("Fetching User Data", 1, True)


logStatus("Fetching Repos Data", 0)
REPOS_DATA = None

try:
	REPOS_DATA = requests.get("https://api.github.com/users/belivipro9x99/repos").json()
except json.JSONDecodeError as error:
	logStatus("Parse Repos Data Failed: Malformed JSON Data", -1, True)
	raise error

logStatus("Fetching Repos Data", 1, True)
##? ============= PLACEHOLDER FUNCTION =============

def updateTime():
	now = datetime.now()
	return now.strftime("%d/%m/%Y %I:%M:%S %p")

def starsCount():
	stars = 0

	for item in REPOS_DATA:
		stars += item["stargazers_count"]

	return stars

def repoCount():
	return len(REPOS_DATA)

def followersCount():
	return USER_DATA["followers"]

def repoLists():
	sortedList = sorted(REPOS_DATA, key = lambda k: k["stargazers_count"], reverse = True)
	counter = 0

	html = """\n<tr>
		<th>#</th>
		<th>Name</th>
		<th>Star</th>
		<th>Size</th>
		<th>Language</th>
		<th>Last Update</th>
		<th></th>
	</tr>\n"""

	for item in sortedList:
		counter += 1
		html += f"""<tr>
			<td style="text-align: right;">{counter}</td>
			<td><a href="{item['html_url']}" target="_blank">{item['name']}</a></td>
			<td style="text-align: right;">{item['stargazers_count']} ⭐</td>
			<td style="text-align: right;">{round(item['size'] / 1024, 2)} MB</td>
			<td>{item['language']}</td>
			<td style="text-align: right;">{item['updated_at']}</td>
			<td style="white-space: pre;">{item['open_issues']} ⚠  |  {item['forks_count']} 🍴</td>
		</tr>\n"""

		if (counter >= 5):
			break

	return html

def runTime():
	return perf_counter()

##? ============= MAIN CODE =============

PLACEHOLDERS = {
	"STARS": starsCount,
	"REPOS": repoCount,
	"FOLLOWERS": followersCount,
	"TIME": updateTime,
	"REPOLISTS": repoLists,
	"RUNTIME": runTime
}

log("INFO", "Generating README file")
logStatus("Opening Template File", 0)
with open("README_TEMPLATE.md", "r", encoding="utf8") as templateFile:
	template = templateFile.read()
	logStatus("Opening Template File", 1, True)

	for key in PLACEHOLDERS:
		logStatus(f"Processing Placeholder: {key}", 0)
		value = PLACEHOLDERS[key]()
		template = template.replace("{{" + key + "}}", str(value))
		logStatus(f"Processing Placeholder: {key}", 1, True)

	logStatus("Writing README File", 0)
	with open("README.md", "w", encoding="utf8") as file:
		file.write(template)
		logStatus("Writing README File", 1, True)