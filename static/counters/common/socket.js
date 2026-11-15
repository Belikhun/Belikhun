// Copyright (c) 2026 Belikhun. All rights reserved.
// Proprietary software: use, copying, modification and distribution are
// prohibited without written permission. See LICENSE at the repository root.

// Stands in for tosu's socket.js. The counters beside this file are the real
// ones from github.com/Belikhun/osu-counters, unchanged; they ask this class for
// a connection to the game, and get an endless made-up play instead. The player
// is real: the profile, the map (my top play) and the mania-tracker ratings are
// copies saved under ../data, served in place of the network.

(() => {
	/** How often each channel sends, in milliseconds. */
	const COMMON_EVERY = 100;
	const PRECISE_EVERY = 50;

	/** My osu! profile, in the mania ruleset, as it stood on 2026-11-15. */
	const PROFILE = {
		id: 13623459,
		name: 'Belikhun',
		mode: { name: 'mania' },
		globalRank: 93857,
		pp: 3039.54,
		accuracy: 95.89,
		level: 70.32,
		countryCode: { name: 'VN' },
		backgroundColour: null,
		banchoStatus: { name: 'playing' }
	};

	/** My top play. The real map runs 81 seconds; this one is cut to 45 so a visitor sees more of it. */
	const MAP = {
		id: 3860593,
		artist: 'kis-kis',
		title: 'ne uchi (Cut Ver.)',
		version: '[4K] you won\'t be saved from people like me',
		firstObject: 1000,
		lastObject: 46000,
		circles: 930,
		holds: 97,
		keys: 4,
		od: 8,
		bpm: 195,
		stars: 4.57
	};

	/** Judgements in the map: a hold is judged at both ends. */
	const JUDGEMENTS = MAP.circles + MAP.holds * 2;

	/** Hit windows of the mania ruleset at this overall difficulty, in milliseconds. */
	const WINDOWS = { geki: 16.5, 300: 64 - 3 * MAP.od, katu: 97 - 3 * MAP.od, 100: 127 - 3 * MAP.od, 50: 151 - 3 * MAP.od };

	/** How long the counters stay hidden between two plays, in milliseconds. */
	const BREAK = 2500;

	/** pp for a full combo at each accuracy, as tosu reports it. */
	const ACCURACY_PP = { 100: 205.3, 99: 192.6, 98: 183.1, 97: 175.2, 96: 168, 95: 161.4 };

	/** The site's colours, handed to each counter as the settings tosu would send. */
	const SETTINGS = {
		accentColor: '#a9d4ec',
		backgroundColor: '#2a2440',
		backgroundOpacity: 100,
		resultBackgroundOpacity: 100,
		borderRadius: 0
	};

	const LABELS = { 'pp': 'pp', 'unstable-rate': 'unstable rate', 'rank-acc': 'rank', 'dan-utils': 'dan' };

	/** The saved answer for each address the counters ask the network for. */
	const SAVED = [
		{ match: '/users/lookup', file: 'lookup.json' },
		{ match: '/skills', file: 'skills.json' },
		{ match: 'map-search-entry', file: 'entry.json' },
		{ match: 'chart-analysis?', file: 'analysis.json' }
	];

	/** A fake open socket: app.js checks readyState and sends filters to it. */
	const OPEN_SOCKET = { readyState: 1, send() {} };

	// added last, so the site's palette wins over the counters' own sheets
	const theme = document.createElement('link');

	theme.rel = 'stylesheet';
	theme.href = '../common/theme.css';
	document.head.append(theme);

	// This listener is added before app.js adds its own, so by the time the
	// counters start, their network layer already reads from ../data.
	window.addEventListener('load', () => {
		// the dan counter paints these from script, so the palette is handed over here as well
		if (typeof Dan !== 'undefined') {
			Dan.SUFFIX_COLORS = { '--': '#a9d4ec', '-': '#c3dcf0', '+': '#ecbcd6', '++': '#f08fb0' };
		}

		if (typeof Net === 'undefined') {
			return;
		}

		Net.request = async (url) => {
			const saved = SAVED.find(({ match }) => url.includes(match));

			if (!saved) {
				return { status: 404, data: null };
			}

			const response = await fetch(`../data/${saved.file}`);

			return { status: 200, data: await response.json() };
		};
	});

	/** A normally distributed number around zero. */
	function gaussian(deviation) {
		const u = 1 - Math.random();
		const v = Math.random();

		return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v) * deviation;
	}

	/** The difficulty of the map over time, for the dan counter's backdrop. */
	function strains() {
		const xaxis = [];
		const data = [];

		for (let time = MAP.firstObject; time <= MAP.lastObject; time += 500) {
			const along = (time - MAP.firstObject) / (MAP.lastObject - MAP.firstObject);

			xaxis.push(time);
			data.push(3 + along * 1.2 + Math.sin(along * 19) * 0.6 + Math.sin(along * 7) * 0.4);
		}

		return { series: [{ name: 'strain', data }], xaxis };
	}

	const GRAPH = strains();

	function newPlay() {
		return { startedAt: performance.now(), errors: [], hits: { 0: 0, 50: 0, 100: 0, 300: 0, geki: 0, katu: 0 }, best: 0 };
	}

	let play = newPlay();

	function judge(off) {
		if (Math.random() < 0.002) {
			return 0;
		}

		return ['geki', 300, 'katu', 100, 50].find((name) => off <= WINDOWS[name]) ?? 0;
	}

	/** Plays every judgement that is due by now, and reports how far into the map the play is. */
	function advance() {
		const live = performance.now() - play.startedAt;
		const progress = Math.min(1, Math.max(0, (live - MAP.firstObject) / (MAP.lastObject - MAP.firstObject)));
		const due = Math.floor(progress * JUDGEMENTS);

		while (play.errors.length < due) {
			// mostly steady, with the odd rushed note
			const error = Math.random() < 0.03
				? gaussian(40)
				: gaussian(11.5) + 1.5;

			play.hits[judge(Math.abs(error))] += 1;
			play.errors.push(Math.round(error * 10) / 10);
		}

		if (live > MAP.lastObject + BREAK * 2) {
			play = newPlay();
		}

		return { live, progress };
	}

	function accuracy() {
		const judged = play.errors.length;
		const { hits } = play;

		if (judged === 0) {
			return 100;
		}

		return (300 * (hits.geki + hits[300]) + 200 * hits.katu + 100 * hits[100] + 50 * hits[50]) / (300 * judged) * 100;
	}

	function unstableRate() {
		const count = play.errors.length;

		if (count < 2) {
			return 0;
		}

		const mean = play.errors.reduce((sum, error) => sum + error, 0) / count;
		const variance = play.errors.reduce((sum, error) => sum + (error - mean) ** 2, 0) / count;

		return Math.sqrt(variance) * 10;
	}

	function rank(value) {
		if (value === 100) {
			return 'X';
		}

		if (value > 95) {
			return 'S';
		}

		return value > 90
			? 'A'
			: 'B';
	}

	/** One message of tosu's v2 api, with only the fields these counters read. */
	function common() {
		const { live, progress } = advance();
		const playing = live < MAP.lastObject + BREAK;
		const value = accuracy();
		const skill = (value / 100) ** 6 * 0.99 ** play.hits[0];
		const current = ACCURACY_PP[100] * skill * progress ** 1.4;

		play.best = Math.max(play.best, current);

		return {
			client: 'lazer',
			state: { name: playing ? 'play' : 'menu' },
			profile: PROFILE,
			beatmap: {
				id: MAP.id,
				artist: MAP.artist,
				title: MAP.title,
				version: MAP.version,
				isConvert: false,
				mode: { name: 'mania' },
				time: { live: Math.round(live), firstObject: MAP.firstObject, lastObject: MAP.lastObject },
				stats: {
					cs: { converted: MAP.keys },
					od: { converted: MAP.od },
					bpm: { common: MAP.bpm },
					stars: { total: MAP.stars },
					objects: { circles: MAP.circles, holds: MAP.holds, sliders: 0, spinners: 0 }
				}
			},
			performance: { accuracy: { ...ACCURACY_PP }, graph: GRAPH },
			play: {
				playerName: playing ? PROFILE.name : '',
				mode: { name: 'mania' },
				mods: { rate: 1 },
				accuracy: value,
				unstableRate: unstableRate(),
				rank: { current: rank(value) },
				hits: { ...play.hits },
				pp: {
					current,
					fc: ACCURACY_PP[100] * skill,
					maxAchievable: ACCURACY_PP[100] * skill,
					maxAchieved: play.best
				}
			},
			resultsScreen: { pp: { current: 0 }, mods: { rate: 1 }, hits: { 0: 0, 50: 0, 100: 0, 300: 0, geki: 0, katu: 0 } }
		};
	}

	class WebSocketManager {
		constructor(host) {
			this.host = host;
			this.sockets = {};
			this.onCommand = undefined;
		}

		api_v2(callback) {
			this.sockets['/websocket/v2'] = OPEN_SOCKET;
			setInterval(() => callback(common()), COMMON_EVERY);
		}

		api_v2_precise(callback) {
			this.sockets['/websocket/v2/precise'] = OPEN_SOCKET;
			setInterval(() => callback({ hitErrors: [...play.errors] }), PRECISE_EVERY);
		}

		commands(callback) {
			this.sockets['/websocket/commands'] = OPEN_SOCKET;
			this.onCommand = callback;
		}

		sendCommand(name) {
			if (name !== 'getSettings') {
				return;
			}

			const counter = window.location.pathname.split('/').filter(Boolean).at(-2);

			// the user card keeps its own colours, except for the rank number's tier; only the panels take the site's
			const message = counter === 'user-card'
				? { overrideRank: 'lustrous' }
				: { ...SETTINGS, label: LABELS[counter] };

			setTimeout(() => this.onCommand?.({ command: name, message }), 0);
		}
	}

	window.WebSocketManager = WebSocketManager;
})();
