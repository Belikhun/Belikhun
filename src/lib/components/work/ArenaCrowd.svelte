<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { gsap } from '#lib/motion/gsap.ts';

	const PLAYERS = 20000;

	/** One dot stands for a hundred players. */
	const DOTS = Array.from({ length: PLAYERS / 100 }, (_, index) => index);

	const FORMAT = new Intl.NumberFormat('en-US');

	let root = $state<HTMLDivElement>();
	let joined = $state(PLAYERS);

	/**
	 * Fills the room: the counter climbs to twenty thousand as the dots light up.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 */
	export function animate(timeline: gsap.core.Timeline, at: number): void {
		const counter = { value: 0 };

		timeline
			.fromTo(
				counter,
				{ value: 0 },
				{
					value: PLAYERS,
					duration: 0.4,
					ease: 'power1.in',
					onUpdate: () => {
						joined = Math.round(counter.value / 10) * 10;
					}
				},
				at
			)
			.from(
				gsap.utils.selector(root!)('.dot'),
				{ opacity: 0.12, scale: 0.4, duration: 0.02, stagger: { amount: 0.38, from: 'random' } },
				at
			);
	}
</script>

<div class="arena" bind:this={root}>
	<p class="count">{FORMAT.format(joined)}</p>
	<p class="caption">players in one game</p>
	<div class="crowd" aria-hidden="true">
		{#each DOTS as dot (dot)}
			<i class="dot"></i>
		{/each}
	</div>
</div>

<style lang="scss">
	.arena {
		display: grid;
		align-content: center;
		gap: 0.5rem;
		height: 100%;
		min-height: 20rem;
		padding: 2rem;
		border-radius: 1.5rem;
		background: var(--purple);
		color: var(--paper);
	}

	.count {
		@include display;
		font-size: clamp(4rem, 8vw, 8rem);
		font-variant-numeric: tabular-nums;
	}

	.caption {
		@include label;
	}

	.crowd {
		display: grid;
		grid-template-columns: repeat(25, 1fr);
		gap: 0.375rem;
		margin-top: 1.5rem;
	}

	.dot {
		aspect-ratio: 1;
		border-radius: 50%;
		background: var(--pink);

		&:nth-child(3n) {
			background: var(--blue);
		}

		&:nth-child(7n) {
			background: var(--paper);
		}
	}
</style>
