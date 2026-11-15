<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { gsap, MOTION } from '#lib/motion/gsap.ts';
	import { releaseIntro } from '#lib/motion/stage.ts';

	import Charm from './Charm.svelte';

	const SEEN_KEY = 'belikhun:seen';
	const MINIMUM_SECONDS = 1.2;
	const NAME = 'belikhun'.split('');

	let root = $state<HTMLDivElement>();
	let percent = $state(0);
	let gone = $state(false);

	function seenBefore(): boolean {
		try {
			return sessionStorage.getItem(SEEN_KEY) === '1';
		} catch {
			return false;
		}
	}

	function markSeen(): void {
		try {
			sessionStorage.setItem(SEEN_KEY, '1');
		} catch {
			// private windows may refuse storage; the loader just plays again
		}
	}

	function avatarDecoded(): Promise<void> {
		const image = new Image();
		image.src = '/img/avatar.webp';

		return image.decode().catch(() => {});
	}

	onMount(() => {
		if (seenBefore() || !window.matchMedia(MOTION).matches) {
			gone = true;
			releaseIntro();

			return;
		}

		document.documentElement.classList.add('is-loading');

		const context = gsap.context(() => {
			const swing = gsap.fromTo(
				'.hang',
				{ rotation: -12 },
				{ rotation: 12, duration: 1.1, ease: 'sine.inOut', yoyo: true, repeat: -1 }
			);

			const counter = { value: 0 };

			const counted = new Promise<void>((resolve) => {
				gsap.to(counter, {
					value: 100,
					duration: MINIMUM_SECONDS,
					ease: 'power1.inOut',
					onUpdate: () => {
						percent = Math.round(counter.value);
					},
					onComplete: resolve
				});
			});

			Promise.all([counted, document.fonts.ready, avatarDecoded()]).then(() => {
				swing.kill();

				gsap.timeline()
					.to('.string', { scaleY: 0, transformOrigin: '50% 0%', duration: 0.25, ease: 'power2.in' })
					.to('.doll', { y: '120vh', rotation: 50, transformOrigin: '50% 50%', duration: 0.7, ease: 'power2.in' }, '<')
					.to('.letter', { yPercent: -180, opacity: 0, stagger: 0.03, duration: 0.45, ease: 'power2.in' }, '<0.05')
					.to('.percent', { opacity: 0, duration: 0.2 }, '<')
					.to(root!, { yPercent: -100, duration: 0.8, ease: 'expo.inOut' }, '>-0.15')
					// the hero waits until the curtain is about halfway up; any sooner and its entrance plays unseen
					.call(releaseIntro, [], '<0.4')
					.call(() => {
						gone = true;
						markSeen();
						document.documentElement.classList.remove('is-loading');
					});
			});
		}, root);

		return () => {
			context.revert();
			document.documentElement.classList.remove('is-loading');
		};
	});
</script>

{#if !gone}
	<div class="loader" bind:this={root} aria-hidden="true">
		<div class="hang">
			<Charm string={150} />
		</div>
		<p class="name">
			{#each NAME as letter, index (index)}
				<span class="letter">{letter}</span>
			{/each}
		</p>
		<p class="percent">{String(percent).padStart(3, '0')} %</p>
	</div>
{/if}

<style lang="scss">
	.loader {
		position: fixed;
		inset: 0;
		z-index: 100;
		display: grid;
		place-content: center;
		justify-items: center;
		gap: 0.75rem;
		background: var(--bg);
	}

	.hang {
		position: absolute;
		top: 0;
		left: 50%;
		width: 4.5rem;
		margin-left: -2.25rem;
		transform-origin: 50% 0%;
	}

	.name {
		@include display;
		margin-top: 12rem;
		font-size: 3rem;
	}

	.letter {
		display: inline-block;
	}

	.percent {
		@include label;
		color: var(--soft);
	}
</style>
