// Copyright (c) 2026 Belikhun. All rights reserved.
// Proprietary software: use, copying, modification and distribution are
// prohibited without written permission. See LICENSE at the repository root.

import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { SplitText } from 'gsap/SplitText';

if (typeof window !== 'undefined') {
	gsap.registerPlugin(ScrollTrigger, SplitText);
}

/** Visitors who have not asked for reduced motion. */
export const MOTION = '(prefers-reduced-motion: no-preference)';

/** Where the pinned scenes run; must match the `stage` mixin in _shared.scss. */
export const DESKTOP_MOTION = `(min-width: 64rem) and ${MOTION}`;

/** Motion that follows a mouse, never a finger. */
export const POINTER_MOTION = `(pointer: fine) and ${MOTION}`;

export { gsap, ScrollTrigger, SplitText };
