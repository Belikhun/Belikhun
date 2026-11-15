<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { gsap, MOTION } from '#lib/motion/gsap.ts';

	let root = $state<HTMLElement>();

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(MOTION, () => {
				gsap.timeline({
					scrollTrigger: { trigger: root, start: 'top bottom', end: 'bottom top', scrub: 0.6 }
				})
					.fromTo('.band', { xPercent: 28 }, { xPercent: -8, ease: 'none' }, 0)
					.fromTo('.words', { xPercent: -30 }, { xPercent: 12, ease: 'none' }, 0)
					.fromTo('.under', { xPercent: -24 }, { xPercent: 6, ease: 'none' }, 0);
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
	}

	.band,
	.under {
		position: absolute;
		left: -20%;
		width: 140%;
		rotate: -7deg;
	}

	.band {
		top: 28%;
		padding: 2rem 0;
		border-radius: 50% 50% 0 0 / 18% 18% 0 0;
		background: var(--band);
	}

	.words {
		@include display;
		padding-left: 22%;
		font-size: clamp(5rem, 17vw, 20rem);
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
