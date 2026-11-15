// Copyright (c) 2026 Belikhun. Licensed under the MIT License.
// See LICENSE at the repository root.

import Lenis from 'lenis';

import { gsap, POINTER_MOTION, ScrollTrigger } from './gsap';

let release: () => void = () => {};
let smooth: Lenis | undefined;

const gate = new Promise<void>((resolve) => {
	release = resolve;
});

const holds: Promise<void>[] = [];

/**
 * Asks the loader to stay up until something has loaded, so it is already
 * there when its scene scrolls into view. Called while a scene mounts.
 *
 * @param asset settles when the thing has loaded or failed
 */
export function holdLoader(asset: Promise<unknown>): void {
	holds.push(asset.then(
		() => {},
		() => {}
	));
}

/** Everything the scenes have asked the loader to wait for so far. */
export function loaderHolds(): Promise<void>[] {
	return [...holds];
}

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
	// Only where there is a mouse or trackpad. Lenis leaves a finger's scrolling to the browser
	// anyway, so a phone gains nothing from it, and with it running a phone could, on some loads,
	// not be swiped into the ending: each fling was pulled back to the same place in off-hours
	// (seen on a Pixel 9 Pro XL, Chrome 157; the pull-back comes from no scroll call of ours).
	if (!window.matchMedia(POINTER_MOTION).matches) {
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
