<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { picture } from '#lib/content/site.ts';
	import { gsap, type Span } from '#lib/motion/gsap.ts';

	/** Real captures of the harbor console, in the order they are dealt. */
	const SCREENS = [
		{ name: 'instances', shot: picture('harbor/instances.webp', 'the list of running instances in the harbor console') },
		{ name: 'pipelines', shot: picture('harbor/pipeline.webp', 'a deploy pipeline run with its jobs and logs') },
		{ name: 'codespaces', shot: picture('harbor/codespace.webp', 'a codespace with the file tree and editor open') },
		{ name: 'monitoring', shot: picture('harbor/monitoring.webp', 'health, requests and response time of one instance') },
		{ name: 'Mèo Béo', shot: picture('harbor/meo-beo-chat.webp', 'a new chat with Mèo Béo, the agent that lives in the console') }
	];

	let root = $state<HTMLDivElement>();

	/**
	 * Deals the console's screens onto the desk one by one, each tab lighting as its screen lands.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 * @param shown the stretch of the timeline over which this card is on screen
	 */
	export function animate(timeline: gsap.core.Timeline, at: number, shown: Span): void {
		const scope = gsap.utils.selector(root!);
		const screens = scope('.screen');
		const tabs = scope('.tab');
		const each = 0.42 / screens.length;

		timeline.fromTo(scope('.desk'), { rotationY: -18, rotationX: 11 }, { rotationY: 2, rotationX: 1, duration: shown.to - shown.from, ease: 'none' }, shown.from);

		screens.forEach((screen, index) => {
			const start = at + index * each;

			if (index === 0) {
				timeline.set(tabs.slice(1), { '--lit': 0 }, at);

				return;
			}

			timeline
				.from(screen, { yPercent: 70, z: 240, rotationX: -24, autoAlpha: 0, duration: each, ease: 'power3.out' }, start)
				.to(tabs[index]!, { '--lit': 1, duration: 0.02 }, start)
				.to(tabs[index - 1]!, { '--lit': 0, duration: 0.02 }, start);
		});
	}
</script>

<div class="harbor" bind:this={root}>
	<ul class="tabs">
		{#each SCREENS as screen (screen.name)}
			<li class="tab">{screen.name}</li>
		{/each}
	</ul>

	<div class="desk">
		{#each SCREENS as screen, index (screen.name)}
			<figure class="screen" style:--order={index}>
				<img src={screen.shot.src} width={screen.shot.width} height={screen.shot.height} alt={screen.shot.alt} loading="lazy" />
			</figure>
		{/each}
	</div>

	<p class="caption">harbor.belikhun.dev · real screens</p>
</div>

<style lang="scss">
	// the console's own colours: deep navy and its orange call to action
	$ground: #0b1220;
	$edge: #2a3a55;
	$muted: #9fb0c8;
	$accent: #ff9900;

	.harbor {
		position: relative;
		display: grid;
		grid-template-rows: auto 1fr auto;
		gap: 1.25rem;
		height: 100%;
		min-height: 20rem;
		padding: 1.5rem;
		border-radius: 1.5rem;
		background: $ground;
		color: var(--paper);
		overflow: hidden;
		perspective: 90rem;
	}

	.tabs {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.tab {
		--lit: 1;
		padding: 0.25rem 0.875rem;
		border-radius: 1rem;
		background: color-mix(in srgb, $accent calc(var(--lit) * 100%), #1a2436);
		color: color-mix(in srgb, $ground calc(var(--lit) * 100%), $muted);
		font-family: var(--mono);
		font-size: 0.75rem;
		font-weight: 500;
	}

	.desk {
		position: relative;
		min-height: 14rem;
		transform-style: preserve-3d;
	}

	.screen {
		position: absolute;
		top: calc(var(--order) * 7%);
		left: calc(var(--order) * 4.5%);
		width: 80%;
		margin: 0;
		border: var(--hairline) solid $edge;
		border-radius: 0.75rem;
		overflow: hidden;
		box-shadow: 0 1.5rem 3rem rgba(0, 0, 0, 0.5);

		img {
			width: 100%;
			height: auto;
		}

		@include below($bp-narrow) {
			top: calc(var(--order) * 9%);
			left: calc(var(--order) * 3%);
			width: 86%;
		}
	}

	.caption {
		@include label;
		position: relative;
		color: $muted;
	}
</style>
