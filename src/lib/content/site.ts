// Copyright (c) 2026 Belikhun. All rights reserved.
// Proprietary software: use, copying, modification and distribution are
// prohibited without written permission. See LICENSE at the repository root.

import media from './media.json';

// House style for every string here: lower case, except product, client and
// country names.

/** A picture under static/img with its intrinsic size. */
export interface Picture {
	src: string;
	width: number;
	height: number;
	alt: string;
}

/** An animated emoji: its file under static/emoji and the character it stands for. */
export interface EmojiMark {
	code: string;
	char: string;
}

/** One phrase of the hero marquee, with the emoji that follows it. */
export interface Phrase {
	text: string;
	emoji?: EmojiMark;
}

/** One chapter of the "who is belikhun" scene. */
export interface Chapter {
	emoji: EmojiMark;
	label: string;
	title: string;
	body: string;
	tags: string[];
}

/** One year on the timeline. */
export interface Stop {
	year: number;
	title: string;
	lines: string[];
}

/** Which visual a work card shows beside its text. */
export type WorkKind = 'luna' | 'harbor' | 'vloom' | 'clover' | 'arena' | 'blink' | 'home' | 'themis' | 'ctms';

/** A place a work card points to: its source, or the running thing itself. */
export interface WorkLink {
	text: string;
	href: string;
}

/** One card in the selected work stack. */
export interface Work {
	kind: WorkKind;
	name: string;
	context: string;
	years: string;
	body: string;
	role: string;
	links?: WorkLink[];
	/** A shorter name for tight places, where the full one would be cut */
	short?: string;
}

/** One row of the "everything else" list. */
export interface Row {
	name: string;
	what: string;
	year: number;
	link?: string;
	preview?: Picture;
}

/**
 * Looks a generated picture up by its path under static/img.
 *
 * @param path as written in scripts/assets.py
 * @param alt what the picture shows
 */
export function picture(path: keyof typeof media, alt: string): Picture {
	const [width, height] = media[path] as [number, number];

	return { src: `/img/${path}`, width, height, alt };
}

export const EMAIL = 'belikhun02@gmail.com';

export const GITHUB = 'https://github.com/Belikhun';

/** The public PGP key, as served from `static/`, and the long id it is known by. */
export const GPG_KEY_FILE = '/belikhun.asc';
export const GPG_KEY_ID = '456F 3B28 3B50 78A9';

/** A video on my YouTube channel: its id there, and the name of its compressed copy under static/video. */
export interface Reel {
	id: string;
	file: string;
	title: string;
}

export const REELS: Reel[] = [
	{ id: 'UYmp129xLUo', file: 'manhunt', title: 'luna event · manhunt 2026 reveal' },
	{ id: 'CNmbDobFEv0', file: 'spring-cleanup', title: 'luna event · spring cleanup 2026 reveal' }
];

export const MARQUEE: Phrase[] = [
	{ text: 'fullstack web engineer', emoji: { code: '1f4bb', char: '💻' } },
	{ text: 'builds free software with', emoji: { code: '2764_fe0f', char: '❤' } }
];

export const CHAPTERS: Chapter[] = [
	{
		emoji: { code: '1f393', char: '🎓' },
		label: 'started at 14',
		title: 'a Pascal program',
		body: 'i started at 14 with a Pascal program that ranked my school\'s classes, so the teachers could stop doing it by hand. it won a provincial prize, and i never stopped building.',
		tags: ['Pascal', '2017', 'school']
	},
	{
		emoji: { code: '1f4a1', char: '💡' },
		label: 'builds platforms',
		title: 'frameworks first',
		body: 'at Videa EdTech i wrote the core of Vloom, a framework that turns Moodle into an app platform. then a frontend framework and a live quiz for 20,000 players on top of it.',
		tags: ['Vloom', 'Clover', 'Vloom Arena']
	},
	{
		emoji: { code: '2693', char: '⚓' },
		label: 'owns the whole thing',
		title: 'down to the servers',
		body: 'i like owning the whole thing: the framework, the servers it runs on, the load test that breaks it and the docs that explain it. this site is served by harbor, a platform i wrote myself.',
		tags: ['harbor', 'luna', 'infrastructure']
	}
];

export const STOPS: Stop[] = [
	{
		year: 2017,
		title: 'HTSD',
		lines: ['a Pascal app for my school\'s Red Star team', '2nd prize, provincial youth innovation contest']
	},
	{
		year: 2018,
		title: 'Themis Web Interface',
		lines: ['the first commit of a five-year project']
	},
	{
		year: 2019,
		title: 'provincial science fair',
		lines: ['2nd prize for Themis Web Interface', 'Deal Hunter Suite ships']
	},
	{
		year: 2020,
		title: 'Hanoi Open University',
		lines: ['information technology', 'a covid tracker extension']
	},
	{
		year: 2021,
		title: 'CTMS+',
		lines: ['an unofficial app for the student portal', 'E-HOU LMS · Opentrack, Korea']
	},
	{
		year: 2022,
		title: 'QCV',
		lines: ['first job: WordPress themes and plugins', 'libraries · metronome', 'Vietcourse and LTV LMS']
	},
	{
		year: 2023,
		title: 'Videa EdTech',
		lines: ['the core of Vloom, written in week one', 'blink']
	},
	{
		year: 2024,
		title: 'client platforms',
		lines: ['ABAII MOOC', 'Viettel Construction LMS', 'a smart home thesis']
	},
	{
		year: 2025,
		title: 'engineer\'s degree',
		lines: ['Hanoi Open University', 'Hong Kong University LMS']
	},
	{
		year: 2026,
		title: 'Manulife',
		lines: ['Clover · Vloom Arena', 'Vloom App Platform', 'harbor · luna']
	}
];

export const WORKS: Work[] = [
	{
		kind: 'luna',
		name: 'luna',
		context: 'personal',
		years: '2026',
		body: 'a Minecraft network for friends. i wrote the console that runs its servers and the 72 plugins they share.',
		role: 'sole author · console + plugins',
		links: [
			{ text: 'public page', href: 'https://mc.belikhun.dev' },
			{ text: 'console', href: 'https://console.mc.belikhun.dev' },
			{ text: 'source', href: 'https://github.com/Belikhun/luna-console' }
		]
	},
	{
		kind: 'harbor',
		name: 'harbor',
		context: 'personal',
		years: '2026',
		body: 'my own hosting platform: codespaces, deploys, domains, a firewall and an ai agent called Mèo Béo. this site runs on it.',
		role: 'sole author',
		links: [{ text: 'console', href: 'https://harbor.belikhun.dev' }]
	},
	{
		kind: 'vloom',
		name: 'Vloom',
		context: 'Videa EdTech',
		years: '2023 → now',
		body: 'a learning platform built on Moodle. i wrote its core framework in my first week and have led its r&d since.',
		role: 'architect'
	},
	{
		kind: 'clover',
		name: 'Clover',
		context: 'Videa EdTech',
		years: '2026',
		body: 'a frontend framework with its own compiler, runtime and editor support.',
		role: 'sole author'
	},
	{
		kind: 'arena',
		name: 'Vloom Arena',
		context: 'Videa EdTech',
		years: '2026',
		body: 'a live quiz built for 20,000 players at once.',
		role: 'sole author'
	},
	{
		kind: 'blink',
		name: 'blink',
		context: 'personal',
		years: '2022 → 2023',
		body: 'my own PHP framework with no dependencies: routing, database, caching and sessions.',
		role: 'sole author',
		links: [{ text: 'source', href: 'https://github.com/Belikhun/blink' }]
	},
	{
		kind: 'home',
		name: 'smart home',
		context: 'graduation thesis',
		years: '2024',
		body: 'ESP32 devices on MicroPython, a Bun server that runs them, a phone app, and an assistant called Bụt that works the house when you tell it how you feel.',
		role: 'sole author',
		links: [
			{ text: 'server', href: 'https://github.com/Belikhun/iot-smart-server' },
			{ text: 'device', href: 'https://github.com/Belikhun/iot-smart-device' },
			{ text: 'app', href: 'https://github.com/Belikhun/iot-smart-app' }
		]
	},
	{
		kind: 'themis',
		name: 'Themis Web Interface',
		short: 'Themis',
		context: 'personal',
		years: '2018 → 2023',
		body: 'contest grading on the web: submit code, watch the ranking move. 36 stars and a provincial prize.',
		role: 'author · 994 commits',
		links: [{ text: 'source', href: 'https://github.com/Belikhun/themis-web-interface' }]
	},
	{
		kind: 'ctms',
		name: 'CTMS+',
		context: 'hobby',
		years: '2021 → 2023',
		body: 'an unofficial, third-party app for my university\'s student portal. not affiliated with the university.',
		role: 'founder · lead developer',
		links: [{ text: 'source', href: 'https://github.com/Belikhun/ctms-plus' }]
	}
];

/** The client project shown as a plain card above the list. */
export const CLIENT_WORK = {
	name: 'Manulife',
	context: 'Videa EdTech · 2026',
	body: 'the learning platform that trains Manulife Vietnam\'s agents: onboarding paths, exams and certificates, team dashboards.',
	role: 'core developer'
};

export const ROWS: Row[] = [
	{ name: 'Vloom App Platform', what: 'flutter apps + ai assistant', year: 2026 },
	{ name: 'libraries', what: 'ui kit', year: 2022, link: 'https://github.com/Belikhun/libraries' },
	{ name: 'metronome', what: 'bpm finder', year: 2022, link: 'https://github.com/Belikhun/metronome' },
	{ name: 'discord-chatgpt', what: 'discord bot', year: 2023, link: 'https://github.com/Belikhun/discord-chatgpt' },
	{
		name: 'Deal Hunter Suite',
		what: 'chrome extension',
		year: 2019,
		preview: picture('rows/deal-hunter-suite.webp', 'Deal Hunter Suite splash screen')
	},
	{ name: 'thi-trac-nghiem', what: 'exam system', year: 2020, link: 'https://github.com/Belikhun/thi-trac-nghiem' },
	{ name: 'covid tracker', what: 'chrome extension', year: 2020, link: 'https://github.com/Belikhun/corona-tracker-extension' },
	{ name: 'BoatRacing', what: 'Minecraft plugin', year: 2025 },
	{ name: 'HTSD', what: 'Pascal', year: 2017 }
];

export const CLIENTS: string[] = [
	'Manulife',
	'Hong Kong University',
	'Viettel Construction',
	'ABAII',
	'Hanoi Open University',
	'Luong The Vinh University',
	'Vietcourse',
	'Opentrack'
];
