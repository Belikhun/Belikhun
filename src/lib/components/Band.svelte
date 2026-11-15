<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { gsap, MOTION } from '#lib/motion/gsap.ts';

	/** How far the ribbon travels each way from the centre, in percent of its own width: one screen, as it is four screens long. */
	const TRAVEL = 25;

	let root = $state<HTMLElement>();

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(MOTION, () => {
				// The words cross the whole screen on the ribbon: out of sight past the left
				// edge, centred when the section is, gone past the right edge. The ribbon is
				// four screens long, so its own ends never come into view.
				gsap.timeline({
					scrollTrigger: { trigger: root, start: 'top bottom', end: 'bottom top', scrub: 0.6 }
				})
					.fromTo('.band', { xPercent: -TRAVEL }, { xPercent: TRAVEL, ease: 'none' }, 0)
					.fromTo('.under', { xPercent: -12 }, { xPercent: 12, ease: 'none' }, 0);
			});
		}, root);

		return () => context.revert();
	});
</script>

<section class="break" bind:this={root}>
	<div class="band">
		<h2 class="words">things i built</h2>
	</div>
	<div class="under" aria-hidden="true"></div>
</section>

<style lang="scss">
	.break {
		position: relative;
		height: 100vh;
		min-height: 32rem;
		overflow: hidden;

		@include below($bp-medium) {
			height: 55vh;
			min-height: 22rem;
		}
	}

	.band,
	.under {
		position: absolute;
		left: -20%;
		width: 140%;
		rotate: -7deg;
	}

	// long enough that it still spans the screen at both ends of its travel; TRAVEL depends on this width
	.band {
		top: 28%;
		left: -150%;
		width: 400%;
		padding: 2rem 0;
		background: var(--band);
	}

	.words {
		@include display;
		font-size: clamp(3.5rem, 13vw, 16rem);
		text-align: center;
		color: var(--ink);
		white-space: nowrap;

		@include below($bp-narrow) {
			white-space: normal;
		}
	}

	.under {
		top: 82%;
		height: 60%;
		background: var(--stage);
	}
</style>
