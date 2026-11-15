<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import type { Picture } from '#lib/content/site.ts';
	import { gsap } from '#lib/motion/gsap.ts';

	let {
		pictures,
		tone = 'lav'
	}: {
		/** The first picture is the base; the rest land on top of it */
		pictures: Picture[];
		tone?: 'lav' | 'blue';
	} = $props();

	let root = $state<HTMLDivElement>();

	/**
	 * Deals the later screenshots onto the first one.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 */
	export function animate(timeline: gsap.core.Timeline, at: number): void {
		const shots = gsap.utils.selector(root!)('.shot');

		timeline
			.from(shots[0]!, { scale: 0.92, autoAlpha: 0, duration: 0.1, ease: 'power2.out' }, at)
			.from(
				shots.slice(1),
				{ yPercent: 60, rotation: 8, autoAlpha: 0, duration: 0.14, stagger: 0.12, ease: 'power3.out' },
				at + 0.1
			);
	}
</script>

<div class="shots {tone}" bind:this={root}>
	{#each pictures as shot, index (shot.src)}
		<img
			class="shot"
			class:portrait={shot.height > shot.width}
			style:--order={index}
			src={shot.src}
			width={shot.width}
			height={shot.height}
			alt={shot.alt}
			loading="lazy"
		/>
	{/each}
</div>

<style lang="scss">
	.shots {
		position: relative;
		height: 100%;
		min-height: 20rem;
		border-radius: 1.5rem;
		background: var(--lav);
		overflow: hidden;

		&.blue {
			background: var(--blue);
		}
	}

	.shot {
		position: absolute;
		top: 10%;
		left: 6%;
		width: 78%;
		height: auto;
		border-radius: 0.75rem;
		box-shadow: 0 1rem 2.5rem rgba(42, 36, 64, 0.28);

		&:not(:first-child) {
			top: auto;
			left: auto;
			right: calc(4% + (var(--order) - 1) * 18%);
			bottom: 6%;
			width: 56%;
		}

		&.portrait:not(:first-child) {
			width: 24%;
		}
	}
</style>
