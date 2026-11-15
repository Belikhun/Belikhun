<!-- Copyright (c) 2026 Belikhun. Licensed under the MIT License.
     See LICENSE at the repository root. -->

<script lang="ts" module>
	/** One download per emoji, however many times it appears on the page. */
	const DOWNLOADS = new Map<string, Promise<unknown>>();

	function download(code: string): Promise<unknown> {
		let pending = DOWNLOADS.get(code);

		if (!pending) {
			pending = fetch(`/emoji/${code}.json`).then((response) => response.json());
			DOWNLOADS.set(code, pending);
		}

		return pending;
	}
</script>

<script lang="ts">
	import { onMount } from 'svelte';

	import { MOTION } from '#lib/motion/gsap.ts';
	import { holdLoader } from '#lib/motion/stage.ts';

	/**
	 * An emoji that moves: the plain character until its animation has loaded,
	 * and for good where motion is reduced. The animations are Noto Animated
	 * Emoji by Google (CC BY 4.0), kept under static/emoji.
	 */

	let {
		code,
		char
	}: {
		/** The animation's file name under static/emoji, such as `2764_fe0f` */
		code: string;
		/** The character it stands for */
		char: string;
	} = $props();

	let host = $state<HTMLSpanElement>();
	let live = $state(false);

	onMount(() => {
		if (!window.matchMedia(MOTION).matches) {
			return;
		}

		let gone = false;
		let stop: (() => void) | undefined;

		const load = (): Promise<void> => Promise.all([import('lottie-web/build/player/lottie_light'), download(code)]).then(([lottie, data]) => {
			if (gone) {
				return;
			}

			const player = lottie.default.loadAnimation({
				container: host!,
				renderer: 'svg',
				loop: true,
				autoplay: false,
				// the player rewrites the data it is given, so each emoji gets its own copy
				animationData: structuredClone(data)
			});

			const seen = new IntersectionObserver(([entry]) => {
				if (entry!.isIntersecting) {
					player.play();
				} else {
					player.pause();
				}
			});

			seen.observe(host!);
			live = true;

			stop = () => {
				seen.disconnect();
				player.destroy();
			};
		}).catch(() => {
			// the plain character stays
		});

		// downloaded behind the loader, so it is already moving when it scrolls into view
		holdLoader(load());

		return () => {
			gone = true;
			stop?.();
		};
	});
</script>

<span class="emoji" class:live bind:this={host}><span class="char">{char}</span></span>

<style lang="scss">
	.emoji {
		display: inline-block;

		&.live {
			width: 1.1em;
			height: 1.1em;
			vertical-align: -0.2em;

			// some animations swing a little past their own box
			:global(svg) {
				overflow: visible;
			}

			.char {
				display: none;
			}
		}
	}
</style>
