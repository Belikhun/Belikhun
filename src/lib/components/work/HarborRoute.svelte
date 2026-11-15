<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { picture } from '#lib/content/site.ts';
	import { gsap } from '#lib/motion/gsap.ts';

	const MASCOT = picture('harbor/meo-beo.webp', 'Mèo Béo, Harbor\'s cat agent');
	const HOPS = ['you', 'nginx', 'Harbor', 'belikhun.dev'];
	const PARTS = ['codespaces', 'deploys', 'domains + tls', 'firewall', 'monitoring', 'Mèo Béo'];

	let root = $state<HTMLDivElement>();

	/**
	 * Sends a request down the route that serves this very page, then lists what else Harbor does.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 */
	export function animate(timeline: gsap.core.Timeline, at: number): void {
		const scope = gsap.utils.selector(root!);

		timeline
			.fromTo(scope('.dot'), { left: '0%' }, { left: '100%', duration: 0.3, ease: 'none' }, at)
			.fromTo(scope('.hop'), { '--lit': 0 }, { '--lit': 1, duration: 0.04, stagger: 0.09 }, at)
			.from(scope('.part'), { autoAlpha: 0, y: '1rem', duration: 0.08, stagger: 0.03 }, at + 0.2)
			.from(scope('.mascot'), { yPercent: 40, autoAlpha: 0, duration: 0.15, ease: 'back.out(1.6)' }, at + 0.3);
	}
</script>

<div class="harbor" bind:this={root}>
	<p class="caption">how this page reached you</p>

	<ol class="route">
		{#each HOPS as hop (hop)}
			<li class="hop">{hop}</li>
		{/each}
		<li class="rail" aria-hidden="true"><i class="dot"></i></li>
	</ol>

	<ul class="parts">
		{#each PARTS as part (part)}
			<li class="part">{part}</li>
		{/each}
	</ul>

	<img class="mascot" src={MASCOT.src} width={MASCOT.width} height={MASCOT.height} alt={MASCOT.alt} loading="lazy" />
</div>

<style lang="scss">
	.harbor {
		position: relative;
		display: grid;
		align-content: center;
		gap: 2rem;
		height: 100%;
		min-height: 20rem;
		padding: 2rem;
		border-radius: 1.5rem;
		background: var(--night);
		color: var(--paper);
		overflow: hidden;
	}

	.caption {
		@include label;
		color: var(--lav);
	}

	.route {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 0.5rem;
		padding-bottom: 1.5rem;
	}

	.hop {
		--lit: 1;
		position: relative;
		z-index: 1;
		padding: 0.5rem 1rem;
		border-radius: 1rem;
		background: color-mix(in srgb, var(--blue) calc(var(--lit) * 100%), #40385c);
		color: color-mix(in srgb, var(--night) calc(var(--lit) * 100%), var(--paper));
		font-family: var(--mono);
		font-size: 0.875rem;
	}

	.rail {
		position: absolute;
		left: 1rem;
		right: 1rem;
		bottom: 0.5rem;
		height: 0.125rem;
		background: #40385c;
	}

	.dot {
		position: absolute;
		top: -0.25rem;
		left: 100%;
		width: 0.625rem;
		height: 0.625rem;
		margin-left: -0.375rem;
		border-radius: 50%;
		background: var(--pink);
	}

	.parts {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		max-width: 70%;
	}

	.part {
		padding: 0.375rem 0.875rem;
		border: var(--hairline) solid #554b78;
		border-radius: 1rem;
		font-size: 0.875rem;
	}

	.mascot {
		position: absolute;
		right: 1rem;
		bottom: 0;
		width: 22%;
		height: auto;
		aspect-ratio: 1;
		margin-bottom: 1rem;
		border: 0.25rem solid var(--lav);
		border-radius: 50%;
		object-fit: cover;
	}
</style>
