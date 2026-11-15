<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { MOTION } from '#lib/motion/gsap.ts';

	/**
	 * A teru teru bōzu charm hanging on a string, drawn by hand the way the ones
	 * on the avatar's dress are: a soft, not quite round head, a small lopsided
	 * cloth, a few marks for a face, flat shadows on one side. It blinks and its
	 * cloth billows on its own. The parts carry classes so a scene can cut the
	 * string or drop the doll.
	 */

	/** The expressions a charm can wear. */
	export type Face = 'calm' | 'happy' | 'sleepy' | 'surprised';

	let {
		string = 120,
		face = 'calm',
		flip = false
	}: {
		/** Length of the string, in the drawing's own units */
		string?: number;
		/** The expression it wears */
		face?: Face;
		/** Mirrors the cloth and its shadows, so two charms side by side are not twins */
		flip?: boolean;
	} = $props();

	/** The four points the hem hangs from, left to right: its two corners and the two dips between them. */
	type Hem = [left: [number, number], first: [number, number], second: [number, number], right: [number, number]];

	/** The hem at rest, blown one way, and blown the other. */
	const REST: Hem = [[5.6, 61.8], [21.8, 67.2], [37.2, 68.8], [54.6, 62.2]];
	const BLOWN: Hem = [[10.5, 64.2], [25.6, 65], [41.6, 70.8], [59.6, 58.2]];
	const DRAWN: Hem = [[1.4, 58.8], [18.2, 69.2], [33.4, 66.8], [50.4, 65.6]];

	/** One sway of the cloth: out one way, back, out the other way, back. */
	const SWAY = [REST, BLOWN, REST, DRAWN, REST];
	const SWAY_SECONDS = 2.8;

	// charms on strings of different lengths blink and sway out of step with each other
	const offset = $derived((string % 7) * -0.6);

	let moving = $state(false);

	function at([x, y]: [number, number], dx = 0, dy = 0): string {
		return `${(x + dx).toFixed(1)} ${(y + dy).toFixed(1)}`;
	}

	/** The cloth's outline, hung from the neck down to a hem. */
	function cloth([left, first, second, right]: Hem): string {
		return [
			`M20.6 32.4 C17.2 41.8 ${at(left, 4.8, -10.2)} ${at(left)}`,
			`C${at(left, 6.2, -1.6)} ${at(first, -5.2, -3.8)} ${at(first)}`,
			`C${at(first, 4.8, -4)} ${at(second, -5.4, -2.6)} ${at(second)}`,
			`C${at(second, 4.8, -4)} ${at(right, -5.4, 4)} ${at(right)}`,
			`C${at(right, -4.6, -9.4)} 43.2 43 39.8 32.8 C34 36.6 26.2 36.8 20.6 32.4 Z`
		].join(' ');
	}

	/** The shadow down the cloth's right side, following the same hem. */
	function shadow([, , second, right]: Hem): string {
		return [
			`M39.8 32.8 C43.2 43 ${at(right, -4.6, -9.4)} ${at(right)}`,
			`C${at(right, -5.4, 4)} ${at(second, 4.8, -4)} ${at(second)}`,
			'C40.4 58.4 40.2 46.4 36.4 35.6 Z'
		].join(' ');
	}

	/** The one crease in the cloth, which leans with its left corner. */
	function crease([left]: Hem): string {
		return `M22.4 44.5 C21.2 51 19.4 56.6 ${at(left, 11.6, -0.4)}`;
	}

	onMount(() => {
		moving = window.matchMedia(MOTION).matches;
	});
</script>

<!-- the cloth is redrawn between hem shapes, so it billows instead of tilting as one piece -->
{#snippet sway(shape: (hem: Hem) => string)}
	{#if moving}
		<animate
			attributeName="d"
			dur="{SWAY_SECONDS}s"
			begin="{offset}s"
			repeatCount="indefinite"
			calcMode="spline"
			keyTimes="0; 0.25; 0.5; 0.75; 1"
			keySplines="0.45 0 0.55 1; 0.45 0 0.55 1; 0.45 0 0.55 1; 0.45 0 0.55 1"
			values={SWAY.map(shape).join('; ')}
		/>
	{/if}
{/snippet}

<svg class="charm" viewBox="0 0 60 {string + 74}" aria-hidden="true">
	<path class="string" d="M30 0 C31.2 {string * 0.3} 28.9 {string * 0.66} 30 {string + 5}" />
	<g class="doll" transform="translate(0 {string})" style:--offset="{offset}s">
		<g transform={flip ? 'translate(60 0) scale(-1 1)' : undefined}>
			<path class="body" d={cloth(REST)}>{@render sway(cloth)}</path>
			<path class="shade" d={shadow(REST)}>{@render sway(shadow)}</path>
			<path class="outline" d={cloth(REST)}>{@render sway(cloth)}</path>
			<path class="fold" d={crease(REST)}>{@render sway(crease)}</path>
			<path class="head" d="M30.4 2.4 C41.2 2 48.8 10 48.2 20.6 C47.7 31 40 38.6 29.4 38.1 C18.8 37.6 11.4 30 11.9 19.4 C12.4 9.4 19.6 2.8 30.4 2.4 Z" />
			<path class="shade" d="M47.6 25.4 C44.6 33.6 37.2 38.4 28.6 38 C37 35.6 42.6 30.6 45.2 23.2 Z" />
			<path class="outline" d="M30.4 2.4 C41.2 2 48.8 10 48.2 20.6 C47.7 31 40 38.6 29.4 38.1 C18.8 37.6 11.4 30 11.9 19.4 C12.4 9.4 19.6 2.8 30.4 2.4 Z" />
		</g>

		{#if face === 'happy'}
			<path class="mark" d="M22 21.2 Q24.2 18.6 26.4 21.2 M33.2 20.7 Q35.4 18.1 37.6 20.7" />
			<path class="mark" d="M27.6 23.8 Q29.9 26.8 32.2 23.6" />
		{:else if face === 'sleepy'}
			<path class="mark" d="M22 20.6 Q24.2 21.9 26.4 20.6 M33.2 20.1 Q35.4 21.4 37.6 20.1" />
			<circle class="mark" cx="30" cy="24.8" r="0.9" />
		{:else}
			<circle class="eye" cx="24.2" cy="20.6" r={face === 'surprised' ? 1.4 : 1.15} />
			<circle class="eye" cx="35.4" cy="20.1" r={face === 'surprised' ? 1.4 : 1.15} />

			{#if face === 'surprised'}
				<circle class="mark" cx="30" cy="25.2" r="1.2" />
			{:else}
				<path class="mark" d="M28.4 24.4 Q30 25.1 31.5 24.2" />
			{/if}
		{/if}
	</g>
</svg>

<style lang="scss">
	// the line colour of the illustration: a dark plum, never black
	$line: #4b3a55;
	$shadow: #d8d2e3;

	.charm {
		display: block;
		width: 100%;
		overflow: visible;
	}

	.string {
		fill: none;
		stroke: var(--ink);
		stroke-width: 0.9;
		stroke-linecap: round;
	}

	// each shape's outline is drawn again over its shadow, so the shadow never eats the line
	.body,
	.head {
		fill: var(--paper);
	}

	.shade {
		fill: $shadow;
	}

	.outline,
	.fold,
	.mark {
		fill: none;
		stroke: $line;
		stroke-linecap: round;
		stroke-linejoin: round;
	}

	.outline {
		stroke-width: 1.1;
	}

	.fold {
		stroke-width: 0.7;
		opacity: 0.55;
	}

	.eye {
		fill: $line;
	}

	.mark {
		stroke-width: 0.9;
	}

	.eye {
		transform-box: fill-box;
		transform-origin: 50% 50%;

		@include motion {
			animation: blink 4.6s linear var(--offset) infinite;
		}
	}

	@keyframes blink {
		0%,
		93%,
		100% {
			transform: scaleY(1);
		}

		96% {
			transform: scaleY(0.1);
		}
	}
</style>
