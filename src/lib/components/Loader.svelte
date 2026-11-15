<!-- Copyright (c) 2026 Belikhun. Licensed under the MIT License.
     See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { gsap, MOTION } from '#lib/motion/gsap.ts';
	import { loaderHolds, releaseIntro } from '#lib/motion/stage.ts';

	import Charm from './Charm.svelte';

	const MINIMUM_SECONDS = 1.2;

	/** The longest the loader waits for the page's assets before lifting anyway. */
	const LONGEST_SECONDS = 12;

	/** How much of the gap to the real progress the number closes each frame. */
	const COUNT_EASE = 0.12;

	/** How long the loader holds at 100 %, so the page behind it settles before the curtain lifts. */
	const SETTLE_SECONDS = 0.6;
	const NAME = 'belikhun'.split('');

	/** The loading bar is a short ruler: this many ticks, every fifth one taller, lit from the left as the page loads. */
	const TICKS = Array.from({ length: 41 }, (_, index) => index);
	const MAJOR_EVERY = 5;

	let root = $state<HTMLDivElement>();
	let percent = $state(0);
	let gone = $state(false);

	/** Settles once a picture on the page has been fetched and decoded, or has failed. */
	function pictureReady(image: HTMLImageElement): Promise<void> {
		const fetched = image.complete
			? Promise.resolve()
			: new Promise<void>((resolve) => {
				image.addEventListener('load', () => resolve(), { once: true });
				image.addEventListener('error', () => resolve(), { once: true });
			});

		return fetched.then(() => image.decode()).catch(() => {});
	}

	/**
	 * Everything the page needs before it can be scrolled without anything
	 * loading late: the fonts, every picture, and whatever the scenes asked for.
	 */
	function assets(): Promise<void>[] {
		return [
			document.fonts.ready.then(() => {}),
			...Array.from(document.images, pictureReady),
			...loaderHolds()
		];
	}

	onMount(() => {
		// the loader is in the page as it is served, so it plays on every load; hiding it only once
		// the scripts are in would show it for a moment and then drop it without its exit
		if (!window.matchMedia(MOTION).matches) {
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

			// The number follows what has really loaded, and never runs ahead of the least time the loader shows.
			const clock = { value: 0 };
			let total = 1;
			let done = 0;
			let shown = 0;
			let finish: () => void = () => {};

			const finished = new Promise<void>((resolve) => {
				finish = resolve;
			});

			gsap.to(clock, { value: 1, duration: MINIMUM_SECONDS, ease: 'power1.inOut' });

			const count = (): void => {
				shown += (Math.min(clock.value, done / total) * 100 - shown) * COUNT_EASE;
				percent = Math.round(shown);

				if (percent >= 100) {
					gsap.ticker.remove(count);
					finish();
				}
			};

			// the scenes mount after the loader, so their requests are gathered a moment later
			const gather = gsap.delayedCall(0.05, () => {
				const waited = assets();

				total = waited.length;

				for (const asset of waited) {
					asset.then(() => {
						done += 1;
					});
				}

				gsap.ticker.add(count);
			});

			// a stalled download never keeps the page behind the loader for good
			const giveUp = gsap.delayedCall(LONGEST_SECONDS, () => {
				done = total;
			});

			finished.then(() => {
				gather.kill();
				giveUp.kill();

				// This runs after the context's own function has returned, so a bare selector would search
				// the whole page: the ending's charms have a string and a doll too, and were dropped with it.
				const own = gsap.utils.selector(root!);

				gsap.timeline({ delay: SETTLE_SECONDS, onStart: () => swing.kill() })
					.addLabel('drop')
					.to(own('.string'), { scaleY: 0, transformOrigin: '50% 0%', duration: 0.25, ease: 'power2.in' })
					.to(own('.doll'), { y: '120vh', rotation: 50, transformOrigin: '50% 50%', duration: 0.7, ease: 'power2.in' }, '<')
					.to(own('.letter'), { yPercent: -180, opacity: 0, stagger: 0.03, duration: 0.45, ease: 'power2.in' }, '<0.05')
					.to(own('.meter i'), { scaleY: 0, duration: 0.3, stagger: { each: 0.008, from: 'center' }, ease: 'power2.in' }, '<')
					.to(own('.percent'), { opacity: 0, duration: 0.2 }, '<')
					// the curtain lifts only once the doll has fallen out of the window; lifting sooner carries it back up mid-fall
					.to(root!, { yPercent: -100, duration: 0.8, ease: 'expo.inOut' }, 'drop+=0.6')
					// the hero waits until the curtain is about halfway up; any sooner and its entrance plays unseen
					.call(releaseIntro, [], '<0.4')
					.call(() => {
						gone = true;
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
			<Charm string={150} face="sleepy" />
		</div>
		<p class="name">
			{#each NAME as letter, index (index)}
				<span class="letter">{letter}</span>
			{/each}
		</p>
		<p class="meter">
			{#each TICKS as tick (tick)}
				<i class:major={tick % MAJOR_EVERY === 0} class:lit={percent >= (tick / (TICKS.length - 1)) * 100 && percent > 0}></i>
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
		// without motion it never shows, not even before the scripts arrive
		display: none;
		place-content: center;
		justify-items: center;
		gap: 0.75rem;
		background: var(--bg);

		@include motion {
			display: grid;
		}
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

	.meter {
		display: flex;
		align-items: flex-end;
		gap: 0.25rem;
		height: 1.5rem;
		margin-top: 0.5rem;

		i {
			width: 0.125rem;
			height: 0.625rem;
			border-radius: 0.125rem;
			background: var(--line);
			transform-origin: 50% 100%;
			transition: background-color 0.3s, height 0.3s var(--ease-out);

			&.major {
				height: 1rem;
			}

			// a lit tick stands a little taller, so the edge of what has loaded reads as a wave moving right
			&.lit {
				height: 1rem;
				background: var(--purple);

				&.major {
					height: 1.5rem;
					background: var(--pink);
				}
			}
		}
	}

	.percent {
		@include label;
		color: var(--soft);
	}
</style>
