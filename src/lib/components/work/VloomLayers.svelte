<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { gsap } from '#lib/motion/gsap.ts';

	/** Top of the stack first, as drawn. */
	const PLATES = [
		{ name: 'LXP', note: 'roadmaps, programs, analytics', tone: 'blue' },
		{ name: 'Workplace', note: 'the admin dashboard', tone: 'lav' },
		{ name: 'Vloom core', note: 'routing, data, events, patches', tone: 'purple' },
		{ name: 'Moodle', note: 'left untouched underneath', tone: 'base' }
	];

	let root = $state<HTMLDivElement>();

	/**
	 * Stacks the platform up from Moodle, in the order it was built.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 */
	export function animate(timeline: gsap.core.Timeline, at: number): void {
		const plates = gsap.utils.selector(root!)('.plate').reverse();

		timeline.from(
			plates,
			{ y: '-6rem', autoAlpha: 0, duration: 0.12, stagger: 0.1, ease: 'power2.out' },
			at
		);
	}
</script>

<div class="vloom" bind:this={root}>
	{#each PLATES as plate (plate.name)}
		<div class="plate {plate.tone}">
			<strong>{plate.name}</strong>
			<span>{plate.note}</span>
		</div>
	{/each}
</div>

<style lang="scss">
	.vloom {
		display: grid;
		align-content: center;
		gap: 1rem;
		height: 100%;
		min-height: 20rem;
		padding: 3rem 2rem;
		border-radius: 1.5rem;
		background: var(--bg);
	}

	.plate {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 1rem;
		padding: 1.25rem 1.5rem;
		border-radius: 1rem;
		background: var(--blue);
		color: var(--night);
		transform: skewY(-6deg);
		box-shadow: 0 0.75rem 1.5rem rgba(42, 36, 64, 0.16);

		strong {
			font-family: var(--display);
			font-size: 1.5rem;
			font-weight: 800;
		}

		span {
			@include label;
		}

		&.lav {
			background: var(--lav);
		}

		&.purple {
			background: var(--purple);
			color: var(--paper);
		}

		&.base {
			background: var(--line);
			color: var(--ink);
			box-shadow: none;
		}
	}
</style>
