// Copyright (c) 2026 Belikhun. All rights reserved.
// Proprietary software: use, copying, modification and distribution are
// prohibited without written permission. See LICENSE at the repository root.

/** A position in the window, in pixels. */
export interface Point {
	x: number;
	y: number;
}

/** What the script in app.html leaves on the window: the pointer it saw before this module loaded, and its listener. */
interface EarlyPointer {
	earlyPointer?: Point | null;
	earlyTrack?: (event: PointerEvent) => void;
}

let last: Point | undefined;

if (typeof window !== 'undefined') {
	const early = window as EarlyPointer;

	last = early.earlyPointer ?? undefined;

	if (early.earlyTrack) {
		window.removeEventListener('pointermove', early.earlyTrack);
	}

	window.addEventListener(
		'pointermove',
		(event) => {
			last = { x: event.clientX, y: event.clientY };
		},
		{ passive: true }
	);
}

/**
 * Where the pointer was last seen. It is tracked from the first paint, before
 * any scene is built, so a scene can start out already facing it instead of
 * swinging round on the first move.
 *
 * @returns the position, or nothing if the pointer has not moved yet
 */
export function lastPointer(): Point | undefined {
	return last;
}
