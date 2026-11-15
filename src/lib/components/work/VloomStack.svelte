<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { gsap, type Span } from '#lib/motion/gsap.ts';

	/** Top of the stack first, as drawn. */
	const PLATES = [
		{ name: 'Arena · Clover', note: 'live quiz, frontend framework' },
		{ name: 'LXP', note: 'roadmaps, programs, analytics' },
		{ name: 'Workplace', note: 'the admin dashboard' },
		{ name: 'Vloom core', note: 'orm, router, events, patcher' },
		{ name: 'Moodle', note: 'left untouched underneath' }
	];

	const CORE = ['orm', 'router', 'di', 'middleware', 'event bus', 'permissions', 'patcher'];

	let root = $state<HTMLDivElement>();

	/**
	 * Stacks the platform up from Moodle in the order it was built, while the flower turns behind it.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 * @param shown the stretch of the timeline over which this card is on screen
	 */
	export function animate(timeline: gsap.core.Timeline, at: number, shown: Span): void {
		const scope = gsap.utils.selector(root!);

		timeline
			.fromTo(scope('.flower'), { rotation: -90 }, { rotation: 90, duration: shown.to - shown.from, ease: 'none' }, shown.from)
			.fromTo(scope('.flower'), { scale: 0.8 }, { scale: 1, duration: 0.5, ease: 'none' }, at)
			.from(scope('.plate').reverse(), { '--lift': '20rem', autoAlpha: 0, duration: 0.1, stagger: 0.07, ease: 'power2.out' }, at)
			.from(scope('.chip'), { autoAlpha: 0, y: '0.75rem', duration: 0.05, stagger: 0.015 }, at + 0.32);
	}
</script>

<div class="vloom" bind:this={root}>
	<img class="flower" src="/img/vloom/vloom-symbol-white.svg" width="195" height="184" alt="" />
	<img class="logo" src="/img/vloom/vloom-logo-white.svg" width="760" height="184" alt="Vloom" />

	<div class="scene">
		<ol class="stack">
			{#each PLATES as plate, index (plate.name)}
				<li class="plate" style:--level={PLATES.length - 1 - index}>
					<strong>{plate.name}</strong>
					<span>{plate.note}</span>
				</li>
			{/each}
		</ol>
	</div>

	<ul class="chips">
		{#each CORE as part (part)}
			<li class="chip">{part}</li>
		{/each}
	</ul>
</div>

<style lang="scss">
	// Vloom's brand colours, from its media kit
	$pink: #f65d6f;
	$pink-light: #ffbbc7;
	$pink-mid: #fa8595;
	$charcoal: #333333;

	.vloom {
		position: relative;
		display: grid;
		grid-template-rows: auto 1fr auto;
		gap: 1rem;
		height: 100%;
		min-height: 20rem;
		padding: 2rem;
		border-radius: 1.5rem;
		background: radial-gradient(circle at 30% 20%, $pink-light, $pink-mid 45%, $pink 85%);
		color: #ffffff;
		overflow: hidden;
	}

	.flower {
		position: absolute;
		right: -18%;
		bottom: -30%;
		width: 80%;
		height: auto;
		opacity: 0.16;
	}

	.logo {
		position: relative;
		width: clamp(8rem, 30%, 12rem);
		height: auto;
	}

	.scene {
		position: relative;
		display: grid;
		place-items: center;
		perspective: 80rem;
	}

	.stack {
		position: relative;
		display: grid;
		width: min(60%, 20rem);
		margin-top: 9rem;
		transform: rotateX(56deg) rotateZ(-38deg);
		transform-style: preserve-3d;
	}

	.plate {
		--lift: 0rem;
		grid-area: 1 / 1;
		display: grid;
		align-content: end;
		gap: 0.375rem;
		aspect-ratio: 16 / 10;
		padding: 1rem 1.25rem;
		border-radius: 1rem;
		background: #ffffff;
		color: $charcoal;
		transform: translateZ(calc(var(--level) * 4.5rem + var(--lift)));
		box-shadow: 0 0 0 var(--hairline) rgba(246, 93, 111, 0.35), -0.5rem 0.75rem 1.5rem rgba(140, 30, 50, 0.28);

		strong {
			font-family: var(--display);
			font-size: 1.25rem;
			font-weight: 800;
			line-height: 1;
		}

		span {
			@include label;
			color: $pink;
		}

		&:last-child {
			background: $charcoal;
			color: #ffffff;

			span {
				color: $pink-light;
			}
		}
	}

	.chips {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		gap: 0.375rem;
	}

	.chip {
		padding: 0.25rem 0.75rem;
		border-radius: 1rem;
		background: rgba(255, 255, 255, 0.24);
		font-family: var(--mono);
		font-size: 0.75rem;
		font-weight: 500;
	}
</style>
