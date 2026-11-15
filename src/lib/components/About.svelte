<!-- Copyright (c) 2026 Belikhun. Licensed under the MIT License.
     See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { CHAPTERS } from '#lib/content/site.ts';
	import { DESKTOP_MOTION, gsap, SplitText } from '#lib/motion/gsap.ts';

	import Emoji from './Emoji.svelte';

	const FADED = 0.16;

	/** Where the chapter swap sits inside each one-unit chapter of the timeline. */
	const SWAP_AT = 0.86;

	let root = $state<HTMLElement>();
	let active = $state(0);

	function pad(value: number): string {
		return String(value).padStart(2, '0');
	}

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(DESKTOP_MOTION, () => {
				const chapters = gsap.utils.toArray<HTMLElement>('.chapter');
				const bar = root!.querySelector('.progress i');
				const figure = root!.querySelector<HTMLElement>('.figure')!;
				const numerals = gsap.utils.toArray<HTMLElement>('.numeral');

				const timeline = gsap.timeline({
					// read from the timeline, not the scroll position: the scrub lags behind the wheel
					onUpdate: () => {
						const time = timeline.time();

						active = Math.min(CHAPTERS.length - 1, Math.floor(time + 1 - SWAP_AT));
						gsap.set(bar, { scaleX: timeline.progress() });

						// the numeral's outline is traced in colour as its chapter is read, and starts over when the next one takes over
						figure.style.setProperty('--read', String(gsap.utils.clamp(0, 1, (time - active) / SWAP_AT)));
					},
					scrollTrigger: {
						trigger: root,
						pin: '.pin',
						start: 'top top',
						end: `+=${CHAPTERS.length * 100}%`,
						scrub: 0.6
					}
				});

				// the handoff from the hero: the scene's parts rise into place, one after another, as it scrolls up to its pin
				gsap.from(['.figure', '.head', '.index', '.chapters'], {
					y: '10rem',
					autoAlpha: 0,
					stagger: 0.12,
					ease: 'power2.out',
					scrollTrigger: { trigger: root, start: 'top 90%', end: 'top 10%', scrub: 0.6 }
				});

				chapters.forEach((chapter, index) => {
					const words = SplitText.create(chapter.querySelector('.body'), { type: 'words' }).words;

					gsap.set(words, { opacity: FADED });
					timeline.to(words, { opacity: 1, duration: 0.1, ease: 'none', stagger: 0.7 / words.length }, index);

					const next = chapters[index + 1];

					if (!next) {
						return;
					}

					gsap.set(next, { autoAlpha: 0 });

					// the numeral changes at the swap itself, while it is rolled out of its window
					timeline
						.to(numerals, { yPercent: -110, duration: 0.08, ease: 'power2.in' }, index + SWAP_AT - 0.08)
						.fromTo(numerals, { yPercent: 110 }, { yPercent: 0, duration: 0.1, ease: 'power3.out', immediateRender: false }, index + SWAP_AT)
						.to(chapter, { autoAlpha: 0, y: '-1.5rem', duration: 0.06, ease: 'power1.in' }, index + SWAP_AT - 0.06)
						.fromTo(next, { autoAlpha: 0, y: '1.5rem' }, { autoAlpha: 1, y: 0, duration: 0.08, ease: 'power1.out' }, index + SWAP_AT);
				});

				timeline.to({}, { duration: 0.15 });
			});
		}, root);

		return () => context.revert();
	});
</script>

<section class="about" id="about" bind:this={root}>
	<div class="pin">
		<div class="figure" aria-hidden="true">
			<!-- drawn as SVG text, so its outline can be traced like a pen stroke; sized in the figure's own units, 100 across -->
			<svg class="numeral" viewBox="0 0 100 76">
				<linearGradient id="about-ink" gradientUnits="userSpaceOnUse" x1="0" y1="76" x2="100" y2="0">
					<stop offset="0" stop-color="var(--pink)" />
					<stop offset="0.5" stop-color="var(--purple)" />
					<stop offset="1" stop-color="var(--blue)" />
				</linearGradient>
				<text x="-3.8" y="68">{pad(active + 1)}</text>
				<text class="read" x="-3.8" y="68">{pad(active + 1)}</text>
			</svg>
		</div>

		<header class="head">
			<h2>who is me?</h2>
			<span class="count">{pad(active + 1)} / {pad(CHAPTERS.length)}</span>
		</header>

		<ol class="index" aria-hidden="true">
			{#each CHAPTERS as chapter, index (chapter.label)}
				<li class:active={index === active}>{pad(index + 1)} · {chapter.label}</li>
			{/each}
		</ol>

		<div class="chapters">
			{#each CHAPTERS as chapter, index (chapter.label)}
				<article class="chapter">
					<span class="digit" aria-hidden="true">{pad(index + 1)}</span>
					<span class="step">{pad(index + 1)} · {chapter.label}</span>
					<h3>
						{chapter.title.split(' ').slice(0, -1).join(' ')}
						<span class="keep">{chapter.title.split(' ').at(-1)}&nbsp;<Emoji code={chapter.emoji.code} char={chapter.emoji.char} /></span>
					</h3>
					<p class="body">{chapter.body}</p>
					<ul class="tags">
						{#each chapter.tags as tag (tag)}
							<li># {tag}</li>
						{/each}
					</ul>
				</article>
			{/each}
			<div class="progress"><i></i></div>
		</div>
	</div>
</section>

<style lang="scss">
	.about {
		@include gutter;
		padding-block: 6rem;

		@include stage {
			padding-block: 0;
		}
	}

	.pin {
		display: grid;
		gap: 2rem;
		max-width: 80rem;
		margin-inline: auto;

		@include stage {
			// the list has a fixed width: sized to its text, it would shift the chapter when the active label turns bold
			grid-template-columns: 30% 13rem 1fr;
			grid-template-rows: auto auto;
			column-gap: 3rem;
			row-gap: 3rem;
			align-content: center;
			height: 100vh;
		}
	}

	// the length of the longest contour of a digit, in the drawing's units: each contour is traced from its own start
	$outline: 260;

	.figure {
		--read: 1;
		display: none;

		@include stage {
			position: relative;
			display: block;
			grid-row: 1 / 3;
			align-self: center;
			container-type: inline-size;
			// the window the numeral rolls through when the chapter changes: it cuts top and bottom only
			clip-path: inset(-0.25rem -50%);
		}
	}

	// sized off its column, so the two digits never reach the chapter index beside them
	.numeral {
		display: block;
		width: 100%;
		overflow: visible;

		text {
			@include display;
			// in the drawing's units: the figure is 100 across
			font-size: 84px;
			// filled with the page and painted over the stroke, which hides the font's inner contours
			fill: var(--bg);
			stroke: var(--line);
			stroke-width: 1.2;
			stroke-linejoin: round;
			paint-order: stroke fill;
		}

		// The same outline in colour over the plain one. One dash as long as a digit's whole outline is
		// pulled along it as the chapter is read, so the colour is drawn on the way a pen would trace it.
		.read {
			stroke: url('#about-ink');
			stroke-linecap: round;
			stroke-dasharray: $outline;
			stroke-dashoffset: calc((1 - var(--read)) * #{$outline});
		}
	}

	.head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 1rem;

		@include stage {
			grid-column: 2 / 4;
		}

		h2 {
			@include display;
			font-size: clamp(2.5rem, 4.5vw, 4rem);
		}
	}

	.count {
		@include label;
		display: none;
		color: var(--soft);

		@include stage {
			display: block;
		}
	}

	.index {
		display: none;

		@include stage {
			display: grid;
			align-content: start;
			gap: 1.5rem;
			font-size: 0.875rem;
			white-space: nowrap;
			padding-left: 1.5rem;
			border-left: 0.125rem solid var(--line);
		}

		li {
			position: relative;
			color: var(--soft);
			opacity: 0.75;
			transition: opacity 0.3s, color 0.3s;

			&::before {
				content: '';
				position: absolute;
				top: -0.25rem;
				bottom: -0.25rem;
				left: -1.625rem;
				width: 0.125rem;
				background: var(--purple);
				transform: scaleY(0);
				transition: transform 0.3s;
			}

			&.active {
				color: var(--ink);
				font-weight: 500;
				opacity: 1;

				&::before {
					transform: scaleY(1);
				}
			}
		}
	}

	.chapters {
		display: grid;
		gap: 3rem;

		@include stage {
			gap: 0;
			align-content: start;
		}
	}

	.chapter {
		display: grid;
		// a fixed column for the number: the three chapters' text then shares one left edge
		grid-template-columns: 6.5rem minmax(0, 1fr);
		column-gap: 1.5rem;
		row-gap: 1rem;
		max-width: 46rem;

		> :not(.digit) {
			grid-column: 2;
		}

		@include below($bp-narrow) {
			grid-template-columns: minmax(0, 1fr);

			> :not(.digit) {
				grid-column: 1;
			}
		}

		@include stage {
			// every chapter in the same cell, so they can cross-fade in place
			grid-area: 1 / 1;
			grid-template-columns: minmax(0, 1fr);

			> :not(.digit) {
				grid-column: 1;
			}
		}

		h3 {
			@include display;
			font-size: clamp(2rem, 3vw, 3rem);
			letter-spacing: -0.01em;
			line-height: 1.1;
		}
	}

	// stacked, each chapter carries its own outlined number in the margin
	.digit {
		@include display;
		grid-row: 1 / span 4;
		color: var(--bg);
		font-size: 5.5rem;
		-webkit-text-stroke: 0.2rem var(--lav);
		paint-order: stroke fill;

		@include below($bp-narrow) {
			grid-row: auto;
			font-size: 4rem;
		}

		@include stage {
			display: none;
		}
	}

	// the last word and its emoji break onto a new line together, never apart
	.keep {
		white-space: nowrap;
	}

	.step {
		@include label;
		color: var(--accent-text);

		@include stage {
			display: none;
		}
	}

	.body {
		font-size: clamp(1.25rem, 2vw, 2rem);
		line-height: 1.55;
	}

	.tags {
		@include label;
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem 1.25rem;
		color: var(--soft);
	}

	.progress {
		display: none;

		@include stage {
			display: block;
			grid-area: 2 / 1;
			height: 0.125rem;
			margin-top: 2rem;
			background: var(--line);
		}

		i {
			display: block;
			height: 100%;
			background: var(--purple);
			transform: scaleX(0);
			transform-origin: 0 50%;
		}
	}
</style>
