<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import Emoji from '#lib/components/Emoji.svelte';
	import { gsap, type Span } from '#lib/motion/gsap.ts';

	/** A whole working site; each line is split into coloured runs. */
	const SOURCE: [tone: string, text: string][][] = [
		[['comment', '// routes/web.php']],
		[['keyword', 'use'], ['plain', ' Blink\\Http\\'], ['type', 'Router'], ['plain', ';']],
		[],
		[['type', 'Router'], ['plain', '::'], ['call', 'GET'], ['plain', '('], ['string', '"/"'], ['plain', ', '], ['keyword', 'fn'], ['plain', ' () => '], ['string', '"hello"'], ['plain', ');']],
		[],
		[['type', 'Router'], ['plain', '::'], ['call', 'GET'], ['plain', '('], ['string', '"/user/{id}"'], ['plain', ', '], ['keyword', 'function'], ['plain', ' ('], ['type', 'int'], ['plain', ' $id) {']],
		[['plain', '	'], ['keyword', 'return'], ['plain', ' '], ['type', 'User'], ['plain', '::'], ['call', 'getByID'], ['plain', '($id);']],
		[['plain', '});']]
	];

	const HOPS = ['request', 'router', 'middleware', 'handler', 'response'];
	const PARTS = ['routing', 'database', 'caching', 'sessions', 'uploads', 'api tokens'];

	let root = $state<HTMLDivElement>();

	/**
	 * Writes the routes, then follows one request through the framework to its answer.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 * @param shown the stretch of the timeline over which this card is on screen
	 */
	export function animate(timeline: gsap.core.Timeline, at: number, shown: Span): void {
		const scope = gsap.utils.selector(root!);

		timeline
			.fromTo(scope('.glint'), { rotation: -90 }, { rotation: 90, duration: shown.to - shown.from, ease: 'none' }, shown.from)
			.from(scope('.line'), { clipPath: 'inset(0 100% 0 0)', duration: 0.04, stagger: 0.02, ease: 'none' }, at)
			.fromTo(scope('.hop'), { '--lit': 0 }, { '--lit': 1, duration: 0.03, stagger: 0.035 }, at + 0.18)
			.fromTo(scope('.spark'), { left: '0%' }, { left: '100%', duration: 0.17, ease: 'none' }, at + 0.18)
			.from(scope('.answer > *'), { autoAlpha: 0, y: '0.5rem', duration: 0.04, stagger: 0.02 }, at + 0.36)
			.from(scope('.part'), { autoAlpha: 0, scale: 0.8, duration: 0.04, stagger: 0.012 }, at + 0.4);
	}
</script>

<div class="blink" bind:this={root}>
	<svg class="glint" viewBox="0 0 100 100" aria-hidden="true">
		<path d="M50 0C54 34 66 46 100 50C66 54 54 66 50 100C46 66 34 54 0 50C34 46 46 34 50 0Z" />
	</svg>

	<header>
		<p class="name"><Emoji code="2728" char="✨" /> blink</p>
		<p class="zero"><strong>0</strong> dependencies</p>
	</header>

	<div class="window">
		<pre><code>{#each SOURCE as line, index (index)}<span class="line">{#each line as [tone, text], run (run)}<span class={tone}>{text}</span>{/each}{#if line.length === 0}&nbsp;{/if}</span>{/each}</code></pre>
	</div>

	<ol class="route">
		{#each HOPS as hop (hop)}
			<li class="hop">{hop}</li>
		{/each}
		<li class="rail" aria-hidden="true"><i class="spark"></i></li>
	</ol>

	<div class="answer">
		<p class="status"><b>GET</b> /user/42 <span>200 ok · 3 ms</span></p>
		<p class="json">{'{ "id": 42, "name": "belikhun" }'}</p>
	</div>

	<ul class="parts">
		{#each PARTS as part (part)}
			<li class="part">{part}</li>
		{/each}
	</ul>
</div>

<style lang="scss">
	$dim: #40385c;

	.blink {
		position: relative;
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
		isolation: isolate;
	}

	// the sparkle of the name, large and faint behind everything
	.glint {
		position: absolute;
		z-index: -1;
		right: -14%;
		bottom: -28%;
		width: 62%;
		height: auto;
		fill: var(--lav);
		opacity: 0.1;
	}

	header {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.5rem 1rem;
	}

	.name {
		font-family: var(--display);
		font-size: 1.75rem;
		font-weight: 800;
	}

	.zero {
		@include label;
		color: var(--lav);

		strong {
			color: var(--pink);
			font-size: 1.5rem;
		}
	}

	.window {
		padding: 1.25rem;
		border-radius: 1rem;
		background: #1c1730;
	}

	pre {
		margin: 0;
		font-family: var(--mono);
		font-size: clamp(0.75rem, 0.95vw, 0.875rem);
		line-height: 1.7;
		overflow-x: auto;
	}

	.line {
		display: block;
		clip-path: inset(0 0 0 0);
		white-space: pre;
		tab-size: 2;
	}

	.comment {
		color: var(--soft);
	}

	.keyword {
		color: var(--pink);
	}

	.type {
		color: var(--blue);
	}

	.call {
		color: var(--lav);
	}

	.string {
		color: #ffd58a;
	}

	.route {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 0.375rem;
		padding-bottom: 1rem;
	}

	.hop {
		--lit: 1;
		position: relative;
		z-index: 1;
		padding: 0.25rem 0.75rem;
		border-radius: 1rem;
		background: color-mix(in srgb, var(--blue) calc(var(--lit) * 100%), #{$dim});
		color: color-mix(in srgb, var(--night) calc(var(--lit) * 100%), var(--paper));
		font-family: var(--mono);
		font-size: 0.75rem;
	}

	.rail {
		position: absolute;
		left: 1rem;
		right: 1rem;
		bottom: 0.25rem;
		height: 0.125rem;
		background: $dim;
	}

	.spark {
		position: absolute;
		top: -0.25rem;
		left: 100%;
		width: 0.625rem;
		height: 0.625rem;
		margin-left: -0.375rem;
		border-radius: 50%;
		background: var(--pink);
	}

	.answer {
		display: grid;
		gap: 0.25rem;
		font-family: var(--mono);
		font-size: 0.875rem;

		b {
			color: var(--blue);
			font-weight: 500;
		}

		span {
			margin-left: 0.5rem;
			color: #9be8a8;
		}
	}

	.json {
		color: var(--lav);
	}

	.parts {
		display: flex;
		flex-wrap: wrap;
		gap: 0.375rem;
	}

	.part {
		padding: 0.25rem 0.75rem;
		border: var(--hairline) solid #554b78;
		border-radius: 1rem;
		font-size: 0.75rem;
	}
</style>
