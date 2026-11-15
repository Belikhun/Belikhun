<!-- Copyright (c) 2026 Belikhun. Licensed under the MIT License.
     See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { GPG_KEY_FILE } from '#lib/content/site.ts';
	import { MOTION } from '#lib/motion/gsap.ts';

	// Falling columns of characters, each one streaming Belikhun's public PGP
	// key in order. It fills its nearest positioned ancestor and only runs
	// while that is on screen. Without motion nothing is drawn.

	/** Milliseconds between two steps of the rain. */
	const STEP_MS = 55;

	/** How much of every earlier glyph is wiped at each step; lower leaves longer trails. */
	const FADE = 0.07;

	/** Glyph size in rem, and the room each one gets as a multiple of that size. */
	const GLYPH_REM = 0.875;
	const COLUMN_WIDTH = 1.1;
	const ROW_HEIGHT = 1.35;

	/** The chance, at each step, that a column which has left the bottom starts again. */
	const RESTART_CHANCE = 0.04;

	let canvas = $state<HTMLCanvasElement>();

	/** Keeps only the key's own characters: the armour's header, footer and blank lines go. */
	function body(armoured: string): string {
		return armoured
			.split(/\r?\n/)
			.filter((line) => line && !line.startsWith('-----') && !line.includes(':'))
			.join('');
	}

	onMount(() => {
		if (!window.matchMedia(MOTION).matches) {
			return;
		}

		const context = canvas!.getContext('2d')!;
		const mono = getComputedStyle(document.documentElement).getPropertyValue('--mono');

		let key = '';
		let glyph = 0;
		let rows: number[] = [];
		let reads: number[] = [];
		let timer: ReturnType<typeof setInterval> | undefined;

		const measure = (): void => {
			const ratio = window.devicePixelRatio;

			glyph = parseFloat(getComputedStyle(document.documentElement).fontSize) * GLYPH_REM * ratio;
			canvas!.width = canvas!.clientWidth * ratio;
			canvas!.height = canvas!.clientHeight * ratio;
			context.font = `500 ${glyph}px ${mono}`;

			const columns = Math.ceil(canvas!.width / (glyph * COLUMN_WIDTH));
			const depth = canvas!.height / (glyph * ROW_HEIGHT);

			// every column starts somewhere above the top and reads the key from its own place
			rows = Array.from({ length: columns }, () => -Math.random() * depth);
			reads = Array.from({ length: columns }, () => Math.floor(Math.random() * key.length));
		};

		const step = (): void => {
			// wipe a little of what is already there, so each glyph fades into the card behind it
			context.globalCompositeOperation = 'destination-out';
			context.fillStyle = `rgba(0, 0, 0, ${FADE})`;
			context.fillRect(0, 0, canvas!.width, canvas!.height);
			context.globalCompositeOperation = 'source-over';
			context.fillStyle = '#ffffff';

			rows.forEach((row, column) => {
				if (row >= 0) {
					context.fillText(key[reads[column]! % key.length]!, column * glyph * COLUMN_WIDTH, row * glyph * ROW_HEIGHT);
				}

				reads[column]! += 1;
				rows[column]! += 1;

				if (row * glyph * ROW_HEIGHT > canvas!.height && Math.random() < RESTART_CHANCE) {
					rows[column] = 0;
				}
			});
		};

		const watcher = new IntersectionObserver(([entry]) => {
			clearInterval(timer);
			timer = undefined;

			if (entry!.isIntersecting && key) {
				timer = setInterval(step, STEP_MS);
			}
		});

		const resizer = new ResizeObserver(measure);

		fetch(GPG_KEY_FILE)
			.then((response) => response.text())
			.then((armoured) => {
				key = body(armoured);

				if (!key) {
					return;
				}

				measure();
				resizer.observe(canvas!);
				watcher.observe(canvas!);
			})
			.catch(() => {
				// the rain is decoration: with no key to read, the card simply stays plain
			});

		return () => {
			clearInterval(timer);
			watcher.disconnect();
			resizer.disconnect();
		};
	});
</script>

<canvas class="rain" bind:this={canvas} aria-hidden="true"></canvas>

<style lang="scss">
	.rain {
		@include fill;
		z-index: -1;
		width: 100%;
		height: 100%;
		opacity: 0.4;
		pointer-events: none;
	}
</style>
