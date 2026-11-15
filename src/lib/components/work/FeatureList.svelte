<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { gsap } from '#lib/motion/gsap.ts';

	let {
		title,
		features
	}: {
		title: string;
		features: string[];
	} = $props();

	let root = $state<HTMLDivElement>();

	/**
	 * Ticks the features off one at a time.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 */
	export function animate(timeline: gsap.core.Timeline, at: number): void {
		const scope = gsap.utils.selector(root!);

		timeline
			.from(scope('li'), { x: '-2rem', autoAlpha: 0, duration: 0.1, stagger: 0.1, ease: 'power2.out' }, at)
			.from(scope('.tick'), { scale: 0, duration: 0.06, stagger: 0.1, ease: 'back.out(3)' }, at + 0.06);
	}
</script>

<div class="features" bind:this={root}>
	<p class="title">{title}</p>
	<ul>
		{#each features as feature (feature)}
			<li><i class="tick" aria-hidden="true">✓</i>{feature}</li>
		{/each}
	</ul>
</div>

<style lang="scss">
	.features {
		display: grid;
		align-content: center;
		gap: 2rem;
		height: 100%;
		min-height: 20rem;
		padding: 2.5rem;
		border-radius: 1.5rem;
		background: var(--blue);
		color: var(--night);
	}

	.title {
		@include label;
	}

	ul {
		display: grid;
		gap: 1rem;
	}

	li {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1.25rem 1.5rem;
		border-radius: 1rem;
		background: var(--paper);
		font-size: 1.25rem;
		font-weight: 500;
	}

	.tick {
		display: grid;
		flex: none;
		place-items: center;
		width: 2rem;
		height: 2rem;
		border-radius: 50%;
		background: var(--purple);
		color: var(--paper);
		font-style: normal;
		font-size: 1rem;
	}
</style>
