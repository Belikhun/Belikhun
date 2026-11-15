<!-- Copyright (c) 2026 Belikhun. Licensed under the MIT License.
     See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { STOPS } from '#lib/content/site.ts';
	import { DESKTOP_MOTION, gsap } from '#lib/motion/gsap.ts';

	import Emoji from './Emoji.svelte';

	const FIRST = STOPS[0]!.year;
	const LAST = STOPS[STOPS.length - 1]!.year;

	/** Blank years drawn on the ruler before the first stop and after the last, so it never ends at the needle. */
	const RULER_MARGIN = 5;

	const RULER_YEARS = Array.from({ length: LAST - FIRST + 1 + RULER_MARGIN * 2 }, (_, index) => FIRST - RULER_MARGIN + index);

	let root = $state<HTMLElement>();
	let active = $state(0);

	/** How much of the ribbon's length is drawn once it reaches each card's far edge, as a share of the whole. */
	let reach: number[] = [];

	/** The ribbon through the cards: its path, and the size of the track it is drawn across, all in pixels. */
	let ribbon = $state({ path: '', width: 1, height: 1 });

	/** The length the ribbon's path is declared to have. Large, because the draw-on moves in whole steps of it: with a length of 1 the ribbon could only be hidden or shown. */
	const DRAWN = 1000;

	/** Halvings used to find where the ribbon passes a card's edge; twenty narrow thousands of pixels down to far less than one. */
	const MEASURE_STEPS = 20;

	/** How far inside a card's edge the ribbon is tucked, and how far past the track's ends it starts and finishes, in rem. */
	const TUCK_REM = 1.5;
	const LEAD_REM = 3;

	/**
	 * Lays the ribbon through the cards where they really are. It comes in from
	 * beyond the left end of the track, runs under each card from edge to edge,
	 * crosses every gap in one S-curve, and leaves past the right end.
	 */
	function trace(track: HTMLElement): void {
		const rem = parseFloat(getComputedStyle(document.documentElement).fontSize);
		const tuck = TUCK_REM * rem;
		const lead = LEAD_REM * rem;

		const cards = Array.from(track.querySelectorAll<HTMLElement>('.stop'), (stop) => ({
			left: stop.offsetLeft + tuck,
			right: stop.offsetLeft + stop.offsetWidth - tuck,
			y: stop.offsetTop + stop.offsetHeight / 2
		}));

		// one S-curve between two points, level where it leaves and level where it arrives
		const sweep = (fromX: number, fromY: number, toX: number, toY: number): string => {
			const middle = (fromX + toX) / 2;

			return `C${middle} ${fromY} ${middle} ${toY} ${toX} ${toY}`;
		};

		const first = cards[0]!;
		const last = cards[cards.length - 1]!;
		const width = track.scrollWidth;
		const height = track.offsetHeight;
		const parts = [`M${-lead} ${height * 0.85}`, sweep(-lead, height * 0.85, first.left, first.y)];

		cards.forEach((card, index) => {
			const next = cards[index + 1];

			parts.push(`L${card.right} ${card.y}`);

			if (next) {
				parts.push(sweep(card.right, card.y, next.left, next.y));
			}
		});

		parts.push(sweep(last.right, last.y, width + lead, height * 0.15));
		ribbon = { path: parts.join(' '), width, height };

		// The ribbon only ever moves rightwards, so the length at which it passes a card's edge can be searched for.
		const measure = document.createElementNS('http://www.w3.org/2000/svg', 'path');

		measure.setAttribute('d', ribbon.path);

		const total = measure.getTotalLength();

		reach = cards.map((card) => {
			let low = 0;
			let high = total;

			for (let step = 0; step < MEASURE_STEPS; step++) {
				const middle = (low + high) / 2;

				if (measure.getPointAtLength(middle).x < card.right) {
					low = middle;
				} else {
					high = middle;
				}
			}

			return low / total;
		});
	}

	/** Where the scene is between the stops, as a year with a fraction: 2019.5 is halfway from the 2019 stop to the next. */
	let reading = $state(LAST);

	const year = $derived(STOPS[active]!.year);

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(DESKTOP_MOTION, () => {
				const track = root!.querySelector<HTMLElement>('.track')!;
				const distance = (): number => track.scrollWidth - window.innerWidth;

				// the ribbon is laid through the cards where they really are, and again whenever the track changes size
				const place = { stop: 0, arrived: 0 };
				const strokes = gsap.utils.toArray<SVGPathElement>('.ribbon .drawn');

				// The ribbon is drawn as far as the card being read and no further: it reaches each card as that card becomes the current one.
				const draw = (): void => {
					const before = Math.min(Math.floor(place.stop), STOPS.length - 2);
					const from = reach[before] ?? 0;
					const drawn = (from + ((reach[before + 1] ?? from) - from) * (place.stop - before)) * place.arrived;

					for (const stroke of strokes) {
						stroke.style.strokeDashoffset = String(DRAWN * (1 - drawn));
					}
				};

				const sized = new ResizeObserver(() => {
					trace(track);
					draw();
				});

				sized.observe(track);
				trace(track);
				draw();

				// the cards and the ruler are driven by one scrubbed timeline, so the ruler glides with the cards
				gsap.timeline({
					scrollTrigger: {
						trigger: root,
						pin: '.pin',
						start: 'top top',
						end: () => `+=${distance()}`,
						scrub: 0.6,
						invalidateOnRefresh: true
					}
				})
					.to(track, { x: () => -distance(), ease: 'none' }, 0)
					.to(
						place,
						{
							stop: STOPS.length - 1,
							ease: 'none',
							onUpdate: () => {
								const before = Math.min(Math.floor(place.stop), STOPS.length - 2);
								const from = STOPS[before]!.year;

								active = Math.round(place.stop);
								reading = from + (STOPS[before + 1]!.year - from) * (place.stop - before);
								draw();
							}
						},
						0
					);

				reading = FIRST;

				// the handoff from the scene before: the heading, the cards and the ruler rise into place as the stage scrolls up to its pin
				gsap.from(['.head', '.track', '.ruler'], {
					y: '10rem',
					autoAlpha: 0,
					stagger: 0.12,
					ease: 'power2.out',
					scrollTrigger: { trigger: root, start: 'top 90%', end: 'top 10%', scrub: 0.6 }
				});

				// while the scene is still arriving, the ribbon comes in from the edge of the window to the first card
				gsap.to(place, {
					arrived: 1,
					ease: 'none',
					onUpdate: draw,
					scrollTrigger: { trigger: root, start: 'top 70%', end: 'top top', scrub: 0.6 }
				});

				return () => sized.disconnect();
			});
		}, root);

		return () => context.revert();
	});
</script>

<section class="timeline" id="timeline" bind:this={root}>
	<div class="pin">
		<header class="head">
			<h2>timeline <Emoji code="23f0" char="⏰" /></h2>
			<span class="span">{FIRST} → {LAST}</span>
		</header>

		{#key year}
			<span class="year" aria-hidden="true">{year}</span>
		{/key}

		<ol class="track">
			<li class="ribbon" aria-hidden="true">
				<svg viewBox="0 0 {ribbon.width} {ribbon.height}">
					<!-- the dashes that run along the ribbon only show where the ribbon has been drawn so far -->
					<mask id="timeline-drawn" maskUnits="userSpaceOnUse" x="0" y="0" width={ribbon.width} height={ribbon.height}>
						<path class="drawn" pathLength={DRAWN} d={ribbon.path} />
					</mask>
					<path class="line drawn" pathLength={DRAWN} d={ribbon.path} />
					<path class="flow" d={ribbon.path} mask="url(#timeline-drawn)" />
				</svg>
			</li>
			{#each STOPS as stop, index (stop.year)}
				<li class="stop" class:active={index === active}>
					<span class="when">{stop.year}</span>
					<span class="mark"><Emoji code={stop.emoji.code} char={stop.emoji.char} /></span>
					<h3>{stop.title}</h3>
					<ul>
						{#each stop.lines as line (line)}
							<li>{line}</li>
						{/each}
					</ul>
				</li>
			{/each}
		</ol>

		<!-- a ruler of years that slides under a needle fixed at the middle of the window -->
		<div class="ruler" aria-hidden="true">
			<ol class="tape" style:--at={reading - RULER_YEARS[0]!}>
				{#each RULER_YEARS as mark (mark)}
					<li class:past={mark < FIRST || mark > LAST} class:active={mark === year}><span>{mark}</span></li>
				{/each}
			</ol>
			<span class="needle"></span>
		</div>
	</div>
</section>

<style lang="scss">
	.timeline {
		padding-block: 6rem;

		@include stage {
			padding-block: 0;
		}
	}

	.pin {
		position: relative;

		@include stage {
			display: flex;
			flex-direction: column;
			justify-content: center;
			height: 100vh;
			overflow: hidden;
		}
	}

	.head {
		@include gutter;
		display: flex;
		align-items: baseline;
		gap: 1.5rem;
		margin-bottom: 3rem;

		@include stage {
			position: absolute;
			top: 6rem;
			left: 0;
			margin: 0;
		}

		h2 {
			@include display;
			font-size: clamp(2.5rem, 4.5vw, 4rem);
		}
	}

	.span {
		@include label;
		color: var(--soft);
	}

	.year {
		display: none;

		@include stage {
			@include display;
			// the backdrop of the whole stage: centred behind the cards, which pass in front of it
			position: absolute;
			top: 54%;
			left: 50%;
			display: block;
			font-size: clamp(14rem, 36vw, 44rem);
			color: var(--bg);
			translate: -50% -50%;
			-webkit-text-stroke: 0.2rem var(--line);
			paint-order: stroke fill;
			animation: roll 0.45s cubic-bezier(0.22, 1, 0.36, 1);
		}
	}

	@keyframes roll {
		from {
			transform: translateY(18%);
			opacity: 0;
		}
	}

	.track {
		@include gutter;
		position: relative;
		display: grid;
		gap: 1.5rem;

		// on a tablet, where one column of cards would be half empty, the stops sit two abreast without the line
		@media (width >= #{$bp-narrow}) and (width < #{$bp-medium}) {
			grid-template-columns: repeat(2, minmax(0, 1fr));
			margin-left: 0;
			padding-left: clamp(1rem, 5vw, 5rem);
			border-left: none !important;

			.when::before {
				display: none;
			}
		}
		border-left: 0.25rem solid var(--pink);
		margin-left: clamp(1rem, 5vw, 5rem);
		padding-left: 1.5rem;

		@include stage {
			display: flex;
			align-items: center;
			gap: 6rem;
			width: max-content;
			margin: 0;
			padding-inline: 14vw;
			border: none;
		}
	}

	.ribbon {
		display: none;

		@include stage {
			@include fill;
			display: block;
			pointer-events: none;
		}

		svg {
			@include fill;
			width: 100%;
			height: 100%;
			overflow: visible;
		}

		path {
			fill: none;
			stroke-width: 0.75rem;
			stroke-linecap: round;
		}

		.drawn {
			stroke: #ffffff;
			// the path's length as the markup declares it (DRAWN), so one dash covers it all; hidden until the scene draws it
			stroke-dasharray: 1000;
			stroke-dashoffset: 1000;
		}

		.line {
			stroke: var(--pink);
		}

		// short dashes travelling along the ribbon, from each card to the next
		.flow {
			stroke: var(--paper);
			stroke-width: 0.2rem;
			stroke-dasharray: 0.5rem 2rem;
			animation: flow 1.1s linear infinite;
		}
	}

	@keyframes flow {
		to {
			stroke-dashoffset: -2.5rem;
		}
	}


	.stop {
		position: relative;
		display: grid;
		align-content: start;
		gap: 0.5rem;
		padding: 1.5rem;
		border: var(--hairline) solid var(--line);
		border-radius: 1.5rem;
		background: var(--surface);

		@include stage {
			flex: none;
			width: 21rem;
			transition: transform 0.5s cubic-bezier(0.22, 1, 0.36, 1), border-color 0.3s;

			&:nth-child(odd) {
				margin-top: 5rem;
			}

			&:nth-child(even) {
				margin-bottom: 5rem;
			}

			&.active {
				border-color: var(--purple);
				transform: translateY(-0.75rem) rotate(-1.5deg);
			}
		}

		h3 {
			// clear of the emoji in the corner
			padding-right: 2.5rem;
			font-size: 1.25rem;
			font-weight: 600;
			line-height: 1.3;
		}

		// the year's emoji, in the card's top right corner
		.mark {
			position: absolute;
			top: 1.25rem;
			right: 1.25rem;
			font-size: 2rem;
			line-height: 1;
		}

		ul {
			display: grid;
			gap: 0.25rem;
			color: var(--soft);
		}
	}

	// stacked, each stop hangs off the line by a dot and leads with its year in display type
	.when {
		@include display;
		color: var(--accent-text);
		font-size: 1.75rem;

		&::before {
			content: '';
			position: absolute;
			top: 1.75rem;
			left: -2.125rem;
			width: 1rem;
			height: 1rem;
			border: 0.25rem solid var(--bg);
			border-radius: 50%;
			background: var(--purple);
		}

		@include stage {
			@include label;

			&::before {
				display: none;
			}
		}
	}

	// one year of the ruler, and the ten divisions drawn inside it
	$year: 12rem;
	$division: $year * 0.1;
	$tick: 0.125rem;

	.ruler {
		display: none;

		@include stage {
			position: absolute;
			left: 0;
			right: 0;
			bottom: 1.5rem;
			display: block;
			height: 4.5rem;
			overflow: hidden;
			// the tape fades out towards both edges of the window
			-webkit-mask-image: linear-gradient(90deg, transparent, #000 22%, #000 78%, transparent);
			mask-image: linear-gradient(90deg, transparent, #000 22%, #000 78%, transparent);
		}
	}

	.tape {
		position: absolute;
		top: 1rem;
		left: 50%;
		display: flex;
		// the year being read sits exactly under the needle
		translate: calc(var(--at) * #{-$year}) 0;

		li {
			position: relative;
			flex: none;
			width: $year;
			height: 3.5rem;
			// the small divisions, hanging from the top edge, each centred on its place like the taller marks over them
			background: linear-gradient(90deg, var(--soft) #{$tick}, transparent #{$tick}) #{$tick * -0.5} 0 / #{$division} 0.625rem repeat-x;
			color: var(--soft);
			transition: color 0.3s;

			// the label hangs under the year's own mark, centred on it
			span {
				@include label;
				position: absolute;
				top: 2.25rem;
				left: 0;
				translate: -50% 0;
			}

			// the year's mark, and the half-year's
			&::before,
			&::after {
				content: '';
				position: absolute;
				top: 0;
				left: 0;
				width: $tick;
				height: 1.5rem;
				margin-left: $tick * -0.5;
				background: var(--ink);
				transition: background-color 0.3s, height 0.3s var(--ease-out);
			}

			&::after {
				left: 50%;
				height: 1rem;
				background: var(--soft);
			}

			&.past {
				opacity: 0.35;
			}

			&.active {
				color: var(--ink);

				&::before {
					height: 2rem;
					background: var(--purple);
				}
			}
		}
	}

	// fixed at the middle of the window: a pin with a point, which the tape slides under
	.needle {
		position: absolute;
		top: 0;
		left: 50%;
		width: 0.125rem;
		height: 3rem;
		margin-left: -0.0625rem;
		border-radius: 0.125rem;
		background: var(--pink);

		&::before {
			content: '';
			position: absolute;
			top: 0;
			left: 50%;
			width: 0.75rem;
			height: 0.625rem;
			background: var(--pink);
			clip-path: polygon(0 0, 100% 0, 50% 100%);
			translate: -50% 0;
		}
	}
</style>
