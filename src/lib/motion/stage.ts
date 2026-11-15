// Copyright (c) 2026 Belikhun. All rights reserved.
// Proprietary software: use, copying, modification and distribution are
// prohibited without written permission. See LICENSE at the repository root.

import Lenis from 'lenis';

import { gsap, MOTION, ScrollTrigger } from './gsap';

let release: () => void = () => {};
let smooth: Lenis | undefined;

const gate = new Promise<void>((resolve) => {
	release = resolve;
});

/** Resolves once the loader has left the screen and the hero may play its intro. */
export function introReady(): Promise<void> {
	return gate;
}

/** Called by the loader when it starts to leave. */
export function releaseIntro(): void {
	release();
}

/**
 * Scrolls the page to a position, gliding there where scrolling is smoothed.
 *
 * @param top the scroll position to reach, in pixels
 */
export function scrollToPosition(top: number): void {
	if (smooth) {
		smooth.scrollTo(top);

		return;
	}

	window.scrollTo({ top });
}

/**
 * Smooths wheel scrolling and keeps ScrollTrigger in step with it. Touch
 * devices and reduced-motion visitors keep native scrolling.
 *
 * @returns a function that stops the smoothing
 */
export function startSmoothScroll(): () => void {
	if (!window.matchMedia(MOTION).matches) {
		return () => {};
	}

	const lenis = new Lenis({ anchors: true, autoRaf: false });

	smooth = lenis;

	const tick = (time: number): void => {
		lenis.raf(time * 1000);
	};

	lenis.on('scroll', ScrollTrigger.update);
	gsap.ticker.add(tick);
	gsap.ticker.lagSmoothing(0);

	return () => {
		gsap.ticker.remove(tick);
		lenis.destroy();
		smooth = undefined;
	};
}
