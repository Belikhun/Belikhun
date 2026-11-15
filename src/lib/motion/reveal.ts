// Copyright (c) 2026 Belikhun. All rights reserved.
// Proprietary software: use, copying, modification and distribution are
// prohibited without written permission. See LICENSE at the repository root.

import { gsap, MOTION } from './gsap.ts';

/** How one element is unveiled when it scrolls into view. */
export interface Reveal {
	/** Seconds to wait after the element comes into view */
	delay?: number;
}

/**
 * Svelte action: wipes an element in from its bottom edge the first time it
 * scrolls into view. Without motion the element is simply there.
 *
 * @param node the element to unveil
 * @param options timing for this element
 * @returns the action's teardown
 */
export function reveal(node: HTMLElement, options: Reveal = {}): { destroy(): void } {
	const media = gsap.matchMedia();

	media.add(MOTION, () => {
		gsap.from(node, {
			clipPath: 'inset(0 0 100% 0)',
			y: '2.5rem',
			duration: 1.1,
			delay: options.delay ?? 0,
			ease: 'expo.out',
			scrollTrigger: { trigger: node, start: 'top 88%' }
		});
	});

	return {
		destroy: () => media.revert()
	};
}

/** How far a picture drifts inside its frame, in percent of its own height each way. */
const DRIFT = 9;

/**
 * Svelte action: lets a picture drift inside its frame as the frame crosses the
 * window, so it moves a little slower than the page. The frame must clip its
 * overflow; the picture is enlarged just enough that its edges never show.
 *
 * @param node the picture
 * @returns the action's teardown
 */
export function parallax(node: HTMLElement): { destroy(): void } {
	const media = gsap.matchMedia();

	media.add(MOTION, () => {
		gsap.fromTo(
			node,
			{ yPercent: -DRIFT, scale: 1 + (DRIFT * 2.4) / 100 },
			{
				yPercent: DRIFT,
				ease: 'none',
				scrollTrigger: { trigger: node.parentElement, start: 'top bottom', end: 'bottom top', scrub: true }
			}
		);
	});

	return {
		destroy: () => media.revert()
	};
}
