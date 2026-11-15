<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { createRig, SOURCE_BOX, VIEW, type Rig } from '#lib/avatar/rig.ts';
	import data from '#lib/content/avatar.json';
	import { gsap, MOTION, ScrollTrigger } from '#lib/motion/gsap.ts';

	/**
	 * The avatar. A flat picture until the rig is ready, and for good where
	 * motion is reduced or WebGL is missing; after that a canvas drawn over it.
	 */

	const ATLAS = '/img/avatar/atlas.webp';

	/** How quickly the head and eyes catch up with where they were asked to look, per frame. */
	const FOLLOW = 0.07;

	const BLINK_EVERY = { min: 2.4, max: 6 };

	/** The canvas shows more of the model than the picture does; these place it over the picture. */
	const FRAME = {
		left: `${((VIEW.x - SOURCE_BOX.x) / SOURCE_BOX.width) * 100}%`,
		top: `${((VIEW.y - SOURCE_BOX.y) / SOURCE_BOX.height) * 100}%`,
		width: `${(VIEW.width / SOURCE_BOX.width) * 100}%`,
		height: `${(VIEW.height / SOURCE_BOX.height) * 100}%`
	};

	let root = $state<HTMLDivElement>();
	let canvas = $state<HTMLCanvasElement>();
	let live = $state(false);

	function loadAtlas(): Promise<HTMLImageElement> {
		const image = new Image();
		image.src = ATLAS;

		return image.decode().then(() => image);
	}

	function animate(rig: Rig): () => void {
		const aim = { x: 0, y: 0 };
		let pointerSeen = false;

		const breathing = gsap.to(rig.pose, { breath: 1, duration: 2.3, ease: 'sine.inOut', yoyo: true, repeat: -1 });

		let blinking: gsap.core.Tween | gsap.core.Timeline | undefined;

		const blink = (): void => {
			const twice = Math.random() < 0.2;

			blinking = gsap.timeline({
				delay: gsap.utils.random(BLINK_EVERY.min, BLINK_EVERY.max),
				repeat: twice ? 1 : 0,
				onComplete: blink
			})
				.to(rig.pose, { eyeOpen: 0, duration: 0.07, ease: 'power2.in' })
				.to(rig.pose, { eyeOpen: 1, duration: 0.13, ease: 'power2.out' });
		};

		const follow = (event: PointerEvent): void => {
			const box = root!.getBoundingClientRect();

			pointerSeen = true;
			aim.x = gsap.utils.clamp(-1, 1, (event.clientX - (box.left + box.width / 2)) / (window.innerWidth / 2));
			aim.y = gsap.utils.clamp(-1, 1, (event.clientY - (box.top + box.height * 0.2)) / (window.innerHeight / 2));
		};

		const tick = (seconds: number, deltaMs: number): void => {
			// with no pointer to follow (touch screens), she looks around slowly by herself
			if (!pointerSeen) {
				aim.x = Math.sin(seconds * 0.45) * 0.6;
				aim.y = Math.sin(seconds * 0.31 + 1) * 0.3;
			}

			rig.pose.angleX += (aim.x - rig.pose.angleX) * FOLLOW;
			rig.pose.angleY += (aim.y - rig.pose.angleY) * FOLLOW;
			rig.pose.lookX += (aim.x - rig.pose.lookX) * FOLLOW * 2;
			rig.pose.lookY += (aim.y - rig.pose.lookY) * FOLLOW * 2;
			rig.render(seconds, deltaMs / 1000);
		};

		const visible = ScrollTrigger.create({
			trigger: root,
			start: 'top bottom',
			end: 'bottom top',
			onToggle: (self) => {
				if (self.isActive) {
					gsap.ticker.add(tick);
				} else {
					gsap.ticker.remove(tick);
				}
			}
		});

		const resized = new ResizeObserver(() => rig.resize());

		resized.observe(canvas!);
		window.addEventListener('pointermove', follow);
		blink();

		return () => {
			window.removeEventListener('pointermove', follow);
			resized.disconnect();
			visible.kill();
			breathing.kill();
			blinking?.kill();
			gsap.ticker.remove(tick);
			rig.destroy();
		};
	}

	onMount(() => {
		if (!window.matchMedia(MOTION).matches) {
			return;
		}

		let stop: (() => void) | undefined;
		let gone = false;

		loadAtlas().then((atlas) => {
			const rig = gone
				? undefined
				: createRig(canvas!, data, atlas);

			if (!rig) {
				return;
			}

			stop = animate(rig);
			rig.render(0, 0);
			live = true;
		}).catch(() => {
			// the flat picture stays
		});

		return () => {
			gone = true;
			stop?.();
		};
	});
</script>

<div class="figure" bind:this={root}>
	<img
		class:hidden={live}
		src="/img/avatar.webp"
		width="708"
		height="1200"
		alt="belikhun's avatar: a girl with long pale blue twin-tails in a lavender dress"
	/>
	<canvas
		bind:this={canvas}
		class:shown={live}
		style:left={FRAME.left}
		style:top={FRAME.top}
		style:width={FRAME.width}
		style:height={FRAME.height}
		aria-hidden="true"
	></canvas>
</div>

<style lang="scss">
	.figure {
		position: relative;
		width: 100%;
		height: 100%;
	}

	img {
		width: 100%;
		height: 100%;
		object-fit: contain;
		object-position: 50% 100%;

		&.hidden {
			visibility: hidden;
		}
	}

	canvas {
		position: absolute;
		visibility: hidden;

		&.shown {
			visibility: visible;
		}
	}
</style>
