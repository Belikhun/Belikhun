<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

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

						// the numeral fills from the bottom as its chapter is read, and empties when the next one takes over
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
						.to(chapter, { autoAlpha: 0, y: '-1.5rem', duration: 0.1, ease: 'power1.in' }, index + SWAP_AT)
						.fromTo(next, { autoAlpha: 0, y: '1.5rem' }, { autoAlpha: 1, y: 0, duration: 0.1, ease: 'power1.out' }, index + SWAP_AT + 0.04);
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
			<span class="numeral">{pad(active + 1)}</span>
			<span class="numeral read">{pad(active + 1)}</span>
		</div>

		<header class="head">
			<h2>who is belikhun?</h2>
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
					<span class="step">{pad(index + 1)} · {chapter.label}</span>
					<h3>{chapter.title} <Emoji code={chapter.emoji.code} char={chapter.emoji.char} /></h3>
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
			grid-template-columns: 26% 20% 1fr;
			grid-template-rows: auto auto;
			column-gap: 3rem;
			row-gap: 3rem;
			align-content: center;
			height: 100vh;
		}
	}

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
		@include display;
		display: block;
		font-size: 84cqw;
		color: transparent;
		-webkit-text-stroke: 0.125rem var(--lav);

		&.read {
			position: absolute;
			top: 0;
			left: 0;
			background: linear-gradient(200deg, var(--blue), var(--lav) 50%, var(--pink));
			background-clip: text;
			-webkit-text-stroke: 0;
			clip-path: inset(calc((1 - var(--read)) * 100%) 0 0 0);
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
			padding-left: 1.5rem;
			border-left: 0.125rem solid var(--line);
		}

		li {
			position: relative;
			color: var(--soft);
			opacity: 0.5;
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
		gap: 1rem;
		max-width: 40rem;

		@include stage {
			// every chapter in the same cell, so they can cross-fade in place
			grid-area: 1 / 1;
		}

		h3 {
			@include display;
			font-size: 2rem;
			letter-spacing: -0.01em;
			line-height: 1.1;
		}
	}

	.step {
		@include label;
		color: var(--purple);

		@include stage {
			display: none;
		}
	}

	.body {
		font-size: clamp(1.25rem, 1.6vw, 1.5rem);
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
