<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { gsap } from '#lib/motion/gsap.ts';

	let {
		file,
		lines
	}: {
		/** The file name shown on the tab */
		file: string;
		lines: string[];
	} = $props();

	let root = $state<HTMLDivElement>();

	/**
	 * Writes the sample out line by line.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 */
	export function animate(timeline: gsap.core.Timeline, at: number): void {
		timeline.from(
			gsap.utils.selector(root!)('.line'),
			{ clipPath: 'inset(0 100% 0 0)', duration: 0.06, stagger: 0.4 / lines.length, ease: 'none' },
			at
		);
	}
</script>

<div class="sample" bind:this={root}>
	<p class="file">{file}</p>
	<pre><code>{#each lines as line, index (index)}<span class="line" class:comment={line.trimStart().startsWith('//')}>{line || ' '}</span>{/each}</code></pre>
</div>

<style lang="scss">
	.sample {
		display: grid;
		align-content: center;
		gap: 1rem;
		height: 100%;
		min-height: 20rem;
		padding: 2rem;
		border-radius: 1.5rem;
		background: var(--night);
		color: var(--paper);
		overflow: hidden;
	}

	.file {
		@include label;
		color: var(--lav);
	}

	pre {
		margin: 0;
		font-family: var(--mono);
		font-size: clamp(0.75rem, 1vw, 1rem);
		line-height: 1.7;
		overflow-x: auto;
	}

	.line {
		display: block;
		clip-path: inset(0 0 0 0);
		white-space: pre;

		&.comment {
			color: var(--soft);
		}
	}
</style>
