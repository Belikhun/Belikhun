#!/usr/bin/env python
# -*- coding: utf-8 -*-

from re import M
from lib import ehook;
from lib.log import log;

from colorama import Fore
log("OKAY", "Imported: colorama")

from datetime import datetime
log("OKAY", "Imported: datetime.datetime")

from time import perf_counter, time
log("OKAY", "Imported: time.perf_counter")

import requests
log("OKAY", "Imported: requests")

import json
log("OKAY", "Imported: json")

import pytz
log("OKAY", "Imported: pytz")

import os
log("OKAY", "Imported: os")

def logStatus(text, status, overWrite = False):
	statusText = [f"{Fore.RED}✗ ERRR", f"{Fore.YELLOW}● WAIT", f"{Fore.GREEN}✓ OKAY"]
	logStatus = ["ERRR", "INFO", "OKAY"]

	log(logStatus[status + 1], "{:58}{}{}".format(text, statusText[status + 1], Fore.RESET), resetCursor = (not overWrite))

USERNAME = "belivipro9x99"
TIME_START = perf_counter()


##? ============= CHECK TOKEN =============
token = os.getenv("GITHUB_TOKEN")
headers = {}
if (token):
	log("OKAY", "Found Github Token")
	headers = { "Authorization": f"Bearer {token}" }


##? ============= FETCH DATA =============
logStatus("Fetching User Data", 0)
USER_DATA = None

try:
	USER_DATA = requests.get(f"https://api.github.com/users/{USERNAME}", headers = headers).json()
except json.JSONDecodeError as error:
	logStatus("Parse User Data Failed: Malformed JSON Data", -1, True)
	raise error

logStatus("Fetching User Data", 1, True)


logStatus("Fetching Repos Data", 0)
REPOS_DATA = None

try:
	REPOS_DATA = requests.get(f"https://api.github.com/users/{USERNAME}/repos", headers = headers).json()
except json.JSONDecodeError as error:
	logStatus("Parse Repos Data Failed: Malformed JSON Data", -1, True)
	raise error

logStatus("Fetching Repos Data", 1, True)


##? ============= PLACEHOLDER FUNCTION =============

def updateTime():
	now = datetime.now()
	now = pytz.timezone("UTC").localize(now)
	now = pytz.timezone("Asia/Ho_Chi_Minh").normalize(now)

	return now.strftime("%d/%m/%Y %I:%M:%S %p (GMT+7)")

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

	html = """\n|#|Name|Star|Size|Language|Last Update||\n|---|---|---:|---:|:---:|---|--|\n"""

	for item in sortedList:
		counter += 1
		html += f"""|{counter}|**[{item['name']}]({item['html_url']})**|{item['stargazers_count']} ⭐|{round(item['size'] / 1024, 2)} MB|{item['language']}|{item['updated_at']}|{item['open_issues']} ⚠  \|  {item['forks_count']} 🍴|\n"""

		if (counter >= 3):
			break

	return html

def contributionsCount():
	counter = 0

	for item in REPOS_DATA:
		msg = f"Fetching {USERNAME}/{item['name']}"

		logStatus(msg, 0)
		contributors = requests.get(f"https://api.github.com/repos/{USERNAME}/{item['name']}/contributors", headers = headers).json()
		logStatus(msg, 1, True)

		for contributor in contributors:
			if (contributor["login"] == USERNAME):
				log("DEBG", f"{Fore.LIGHTBLUE_EX}{USERNAME}/{item['name']}{Fore.LIGHTWHITE_EX}: {contributor['contributions']} contributions")
				counter += contributor["contributions"]
	
	return counter

def runTime():
	return "{:.4f}".format(perf_counter() - TIME_START)

##? ============= MAIN CODE =============

PLACEHOLDERS = {
	"STARS": starsCount(),
	"REPOS": repoCount(),
	"FOLLOWERS": followersCount(),
	"TIME": updateTime(),
	"REPOLISTS": repoLists(),
	"RUNTIME": runTime(),
	"COMMITS": contributionsCount()
}

def processFile(input, output):
	logStatus(f"Opening {input}", 0)
	with open(input, "r", encoding="utf8") as templateFile:
		template = templateFile.read()
		logStatus(f"Opening {input}", 1, True)

		for key in PLACEHOLDERS:
			logStatus(f"Processing Placeholder: {key}", 0)
			value = PLACEHOLDERS[key]
			template = template.replace("{{" + key + "}}", str(value))
			logStatus(f"Processing Placeholder: {key}", 1, True)

		logStatus(f"Writing {output}", 0)
		with open(output, "w", encoding="utf8") as file:
			file.write(template)
			logStatus(f"Writing {output}", 1, True)

log("INFO", "Generating README File")
processFile("README_TEMPLATE.md", "README.md")

log("INFO", "Generating Header Image")
processFile("assets/img/header.svg", "header.svg")