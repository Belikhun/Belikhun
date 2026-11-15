<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { gsap, type Span } from '#lib/motion/gsap.ts';

	// spelled in two halves: a whole script tag inside this block would end it
	const SCRIPT = 'scr' + 'ipt';

	/** A whole Clover component; each line is split into coloured runs. */
	const SOURCE: [tone: string, text: string][][] = [
		[['tag', `<${SCRIPT}`], ['attr', ' lang'], ['plain', '='], ['string', '"ts"'], ['tag', '>']],
		[['plain', '	'], ['keyword', 'let'], ['plain', ' count = '], ['rune', '$state'], ['plain', '(0);']],
		[['plain', '	'], ['keyword', 'let'], ['plain', ' double = '], ['rune', '$derived'], ['plain', '(count * 2);']],
		[['tag', `</${SCRIPT}>`]],
		[],
		[['tag', '<button'], ['attr', ' onclick'], ['plain', '={() => count++}'], ['tag', '>']],
		[['plain', '	clicked {count} times']],
		[['tag', '</button>']],
		[['tag', '<p>'], ['plain', 'doubled: {double}'], ['tag', '</p>']]
	];

	const STAGES = ['compiler', 'runtime', 'router', 'ui kit', 'language server', 'vs code'];

	const CLICKS = 7;

	let root = $state<HTMLDivElement>();
	let count = $state(CLICKS);

	/**
	 * Writes the component out, sends it through the compiler, then clicks the running result.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 * @param shown the stretch of the timeline over which this card is on screen
	 */
	export function animate(timeline: gsap.core.Timeline, at: number, shown: Span): void {
		const scope = gsap.utils.selector(root!);
		const clicks = { made: 0 };

		timeline
			.fromTo(scope('.leaf'), { rotation: -70 }, { rotation: 110, duration: shown.to - shown.from, ease: 'none' }, shown.from)
			.from(scope('.line'), { clipPath: 'inset(0 100% 0 0)', duration: 0.04, stagger: 0.02, ease: 'none' }, at)
			.from(scope('.stage'), { autoAlpha: 0, x: '-0.75rem', duration: 0.04, stagger: 0.02 }, at + 0.16)
			.from(scope('.result'), { scale: 0.7, autoAlpha: 0, duration: 0.08, ease: 'back.out(2)' }, at + 0.22)
			.fromTo(
				clicks,
				{ made: 0 },
				{
					made: CLICKS,
					duration: 0.2,
					ease: `steps(${CLICKS})`,
					onUpdate: () => {
						count = Math.round(clicks.made);
					}
				},
				at + 0.3
			);
	}
</script>

<div class="clover" bind:this={root}>
	<img class="leaf" src="/img/clover/clover-symbol.svg" width="200" height="200" alt="" />

	<header>
		<img class="symbol" src="/img/clover/clover-symbol.svg" width="200" height="200" alt="" />
		<img class="wordmark" src="/img/clover/clover-wordmark-white.svg" width="602" height="145" alt="Clover" />
	</header>

	<div class="bench">
		<div class="window">
			<p class="file">Counter.clover</p>
			<pre><code>{#each SOURCE as line, index (index)}<span class="line">{#each line as [tone, text], run (run)}<span class={tone}>{text}</span>{/each}{#if line.length === 0}&nbsp;{/if}</span>{/each}</code></pre>
		</div>

		<div class="result" aria-hidden="true">
			<p class="file">in the browser</p>
			<span class="button">clicked {count} times</span>
			<span class="doubled">doubled: {count * 2}</span>
		</div>
	</div>

	<ul class="stages">
		{#each STAGES as stage (stage)}
			<li class="stage">{stage}</li>
		{/each}
	</ul>
</div>

<style lang="scss">
	// Clover's brand colours, from the Vloom media kit
	$green: #2f9e44;
	$deep: #1e7a34;
	$pale: #d9f7c4;
	$leaf: #8fd96c;
	$ink: #0f2e17;

	.clover {
		position: relative;
		display: grid;
		grid-template-rows: auto 1fr auto;
		gap: 1.25rem;
		height: 100%;
		min-height: 20rem;
		padding: 2rem;
		border-radius: 1.5rem;
		background: linear-gradient(160deg, $green, $deep);
		color: #ffffff;
		overflow: hidden;
	}

	.leaf {
		position: absolute;
		right: -14%;
		bottom: -26%;
		width: 70%;
		height: auto;
		opacity: 0.25;
	}

	header {
		position: relative;
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.symbol {
		width: 3rem;
		height: 3rem;
		padding: 0.25rem;
		border-radius: 50%;
		background: #ffffff;
	}

	.wordmark {
		width: auto;
		height: 2.25rem;
	}

	.bench {
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
		align-items: center;
		gap: 1rem;

		@include below($bp-narrow) {
			grid-template-columns: minmax(0, 1fr);
		}
	}

	.window,
	.result {
		display: grid;
		gap: 0.75rem;
		padding: 1.25rem;
		border-radius: 1rem;
		box-shadow: 0 1rem 2.5rem rgba(8, 40, 16, 0.35);
	}

	.window {
		background: $ink;
	}

	.file {
		@include label;
		color: $leaf;
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

	.tag,
	.keyword {
		color: $leaf;
	}

	.attr {
		color: $pale;
	}

	.string {
		color: #ffd58a;
	}

	.rune {
		color: #ffffff;
		font-weight: 700;
	}

	.result {
		justify-items: start;
		background: #ffffff;
		color: $ink;

		.file {
			color: $green;
		}
	}

	.button {
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
		background: $green;
		color: #ffffff;
		font-weight: 500;
		font-variant-numeric: tabular-nums;
	}

	.doubled {
		font-family: var(--mono);
		font-size: 0.875rem;
		font-variant-numeric: tabular-nums;
	}

	.stages {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		gap: 0.375rem;
	}

	.stage {
		padding: 0.25rem 0.75rem;
		border-radius: 1rem;
		background: rgba(255, 255, 255, 0.2);
		font-family: var(--mono);
		font-size: 0.75rem;
		font-weight: 500;
	}
</style>
