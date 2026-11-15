<!-- Copyright (c) 2026 Belikhun. Licensed under the MIT License.
     See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { picture, REELS } from '#lib/content/site.ts';
	import { DESKTOP_MOTION, gsap, MOTION, ScrollTrigger } from '#lib/motion/gsap.ts';
	import { parallax, reveal } from '#lib/motion/reveal.ts';
	import { holdLoader } from '#lib/motion/stage.ts';

	import Emoji from './Emoji.svelte';

	const LANTERN = picture('luna/wall/lantern.webp', 'a lantern over luna\'s survival world');
	/**
	 * My tosu counters, running as they do on stream: the real code from
	 * github.com/Belikhun/osu-counters under static/counters, fed a made-up play.
	 * Each is framed at the size its metadata asks for.
	 */
	const COUNTERS = {
		pp: { src: '/counters/pp/index.html', title: 'my pp counter, drawing pp over a play', width: 380, height: 270 },
		unstableRate: { src: '/counters/unstable-rate/index.html', title: 'my unstable rate counter, a histogram of hit timing', width: 380, height: 226 },
		rank: { src: '/counters/rank-acc/index.html', title: 'my rank and accuracy counter', width: 380, height: 152 },
		userCard: { src: '/counters/user-card/index.html', title: 'my user card, showing my osu! profile', width: 420, height: 108 },
		dan: { src: '/counters/dan-utils/index.html', title: 'my dan counter, tracking a play against my dan rating', width: 380, height: 360 }
	};

	type Frame = (typeof COUNTERS)[keyof typeof COUNTERS];

	const BOTS = ['bard-bot', 'discord-chatgpt', 'discord-accountant', 'market-tracker'];

	/** Piano roll notes: column, row and length on a 16 by 7 grid. */
	const NOTES = [
		[1, 5, 2], [3, 4, 1], [4, 3, 3], [7, 5, 1], [8, 2, 2], [10, 4, 2], [12, 1, 3], [13, 6, 2],
		[2, 7, 1], [6, 6, 2], [9, 7, 1], [15, 3, 2]
	];

	/** Video timeline clips: track, start and length on a 12-column grid. */
	const CLIPS = [
		[1, 1, 4], [1, 5, 3], [1, 9, 4], [2, 2, 6], [2, 9, 3], [3, 1, 2], [3, 4, 5], [3, 10, 2]
	];

	let root = $state<HTMLElement>();
	/** How long to wait between loading one counter or video and the next, so no two start up in the same moment. */
	const PRELOAD_GAP_MS = 120;

	const FRAMES: Frame[] = Object.values(COUNTERS);

	/** Every counter, then every video: the order they are loaded in. */
	const PIECES = FRAMES.length + REELS.length;

	/** How many pieces have been put on the page so far, and how many of those have finished loading. */
	let loaded = $state(0);
	let settled = 0;
	let allSettled: () => void = () => {};

	/** Counts a counter or a video as loaded, whether it loaded or failed. */
	function settle(): void {
		settled += 1;

		if (settled >= PIECES) {
			allSettled();
		}
	}

	const videos = new Set<HTMLVideoElement>();
	let onScreen = false;

	/** Plays a video only while the section is on screen; off screen it stays loaded but paused. */
	function screened(node: HTMLVideoElement): { destroy(): void } {
		videos.add(node);

		if (onScreen) {
			node.play().catch(() => {});
		}

		return { destroy: () => videos.delete(node) };
	}

	/** Keeps a counter at the size it was designed for and scales the whole frame down to fit its card. */
	function fit(node: HTMLElement, frame: Frame): { destroy(): void } {
		const resized = new ResizeObserver(() => {
			node.style.setProperty('--scale', String(node.clientWidth / frame.width));
		});

		resized.observe(node);

		return { destroy: () => resized.disconnect() };
	}

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(MOTION, () => {
				gsap.from('.tile', {
					clipPath: 'inset(100% 0 0 0 round 1.5rem)',
					y: '4rem',
					duration: 1.1,
					ease: 'expo.out',
					stagger: 0.07,
					scrollTrigger: { trigger: '.wall', start: 'top 85%' }
				});

				const looping = [
					gsap.fromTo('.playhead', { left: '0%' }, { left: '100%', duration: 6, ease: 'none', repeat: -1 }),
					gsap.to('.keys kbd', {
						y: '0.25rem',
						boxShadow: '0 0.125rem 0 var(--purple)',
						duration: 0.07,
						ease: 'power1.in',
						yoyo: true,
						repeat: -1,
						repeatDelay: 0.22,
						stagger: 0.16
					}),
					gsap.fromTo('.online', { opacity: 0.4 }, { opacity: 1, duration: 0.9, ease: 'sine.inOut', yoyo: true, repeat: -1, stagger: 0.3 })
				];

				// The counters and videos are loaded behind the loader, one after another: loading them
				// all on the first scroll into the section froze the page for a moment.
				let waiting: ReturnType<typeof setTimeout> | undefined;

				holdLoader(new Promise<void>((resolve) => {
					allSettled = resolve;
				}));

				const preload = (): void => {
					if (loaded >= PIECES) {
						return;
					}

					loaded += 1;
					waiting = setTimeout(preload, PRELOAD_GAP_MS);
				};

				preload();

				// the loops and the videos only run while the section is on screen
				ScrollTrigger.create({
					trigger: root,
					start: 'top bottom',
					end: 'bottom top',
					onToggle: (self) => {
						onScreen = self.isActive;

						// whatever has not been loaded by the time the section is reached is loaded now
						if (self.isActive) {
							loaded = PIECES;
						}

						for (const loop of looping) {
							loop.paused(!self.isActive);
						}

						for (const video of videos) {
							if (self.isActive) {
								video.play().catch(() => {});
							} else {
								video.pause();
							}
						}
					}
				});

				return () => clearTimeout(waiting);
			});

			media.add(DESKTOP_MOTION, () => {
				gsap.utils.toArray<HTMLElement>('.column').forEach((column, index) => {
					const drift = index % 2 === 0 ? 5 : -5;

					gsap.fromTo(
						column,
						{ y: `${drift}rem` },
						{
							y: `${-drift}rem`,
							ease: 'none',
							scrollTrigger: { trigger: root, start: 'top bottom', end: 'bottom top', scrub: 0.6 }
						}
					);
				});
			});
		}, root);

		return () => context.revert();
	});
</script>

{#snippet counter(frame: Frame)}
	<div class="frame" style:aspect-ratio="{frame.width} / {frame.height}" use:fit={frame}>
		{#if loaded > FRAMES.indexOf(frame)}
			<iframe src={frame.src} title={frame.title} width={frame.width} height={frame.height} onload={settle} onerror={settle}></iframe>
		{/if}
	</div>
{/snippet}

<section class="off" id="off-hours" bind:this={root}>
	<header>
		<h2 use:reveal>off-hours <Emoji code="1f47e" char="👾" /></h2>
		<p>when i'm not shipping i'm clicking circles and writing the counters that sit around them, making noise in FL Studio, cutting videos, or running a Minecraft network for friends.</p>
	</header>

	<!-- my two event reveal videos, playing muted on a loop while the section is on screen; a still frame until they are loaded -->
	<div class="reels">
		{#each REELS as reel, index (reel.id)}
			<a class="reel" href="https://www.youtube.com/watch?v={reel.id}" target="_blank" rel="noreferrer" use:reveal>
				<img src="/video/{reel.file}.jpg" width="1280" height="720" alt="" />
				{#if loaded > FRAMES.length + index}
					<video muted loop playsinline preload="auto" use:screened onloadeddata={settle} onerror={settle} poster="/video/{reel.file}.jpg" aria-label={reel.title}>
						<source src="/video/{reel.file}.av1.mp4" type="video/mp4; codecs=av01.0.05M.10" />
						<source src="/video/{reel.file}.h264.mp4" type="video/mp4; codecs=avc1.640020" />
					</video>
				{/if}
				<span class="caption">{reel.title} ↗</span>
			</a>
		{/each}
	</div>

	<div class="wall">
		<div class="column">
			<figure class="tile counter">
				{@render counter(COUNTERS.pp)}
				<figcaption>osu! · my pp counter</figcaption>
			</figure>
			<figure class="tile counter">
				{@render counter(COUNTERS.userCard)}
				<figcaption>osu! · my user card</figcaption>
			</figure>
			<figure class="tile keypad">
				<div class="keys" aria-hidden="true">
					<kbd>z</kbd>
					<kbd>x</kbd>
				</div>
				<figcaption>a keypad i built on an arduino <Emoji code="26a1" char="⚡" /></figcaption>
			</figure>
		</div>

		<div class="column">
			<figure class="tile roll">
				<div class="notes" aria-hidden="true">
					{#each NOTES as [column, row, length], index (index)}
						<i style:grid-column="{column} / span {length}" style:grid-row={row}></i>
					{/each}
					<b class="playhead"></b>
				</div>
				<figcaption>FL Studio <Emoji code="1f3b6" char="🎶" /></figcaption>
			</figure>
			<figure class="tile picture">
				<img src={LANTERN.src} width={LANTERN.width} height={LANTERN.height} alt={LANTERN.alt} use:parallax />
				<figcaption>luna</figcaption>
			</figure>
		</div>

		<div class="column">
			<figure class="tile counter">
				{@render counter(COUNTERS.unstableRate)}
				<figcaption>osu! · my unstable rate counter</figcaption>
			</figure>
			<figure class="tile counter">
				{@render counter(COUNTERS.rank)}
				<figcaption>osu! · my rank and accuracy counter</figcaption>
			</figure>
			<figure class="tile edit">
				<div class="clips" aria-hidden="true">
					{#each CLIPS as [track, start, length], index (index)}
						<i class="track-{track}" style:grid-row={track} style:grid-column="{start} / span {length}"></i>
					{/each}
					<b class="playhead"></b>
				</div>
				<figcaption>video edits <Emoji code="1f3ac" char="🎬" /></figcaption>
			</figure>
		</div>

		<div class="column">
			<figure class="tile counter">
				{@render counter(COUNTERS.dan)}
				<figcaption>osu!mania · my dan counter</figcaption>
			</figure>
			<figure class="tile bots">
				<ul>
					{#each BOTS as bot (bot)}
						<li><i class="online"></i>{bot}</li>
					{/each}
				</ul>
				<figcaption>discord bots, hosted on harbor <Emoji code="1f916" char="🤖" /></figcaption>
			</figure>
		</div>
	</div>
</section>

<style lang="scss">
	.off {
		@include gutter;
		display: grid;
		gap: 4rem;
		padding-block: 6rem 10rem;
		overflow: hidden;
	}

	header {
		display: grid;
		gap: 1.5rem;
		max-width: 40rem;

		h2 {
			@include display;
			font-size: clamp(2.5rem, 6vw, 6rem);
		}

		p {
			font-size: 1.25rem;
		}
	}

	.reels {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 1.5rem;

		@include below($bp-narrow) {
			grid-template-columns: minmax(0, 1fr);
		}
	}

	.reel {
		position: relative;
		display: grid;
		align-content: end;
		justify-items: start;
		aspect-ratio: 16 / 9;
		padding: 1.25rem;
		border-radius: 1.5rem;
		background: var(--night);
		overflow: hidden;

		img,
		video {
			@include fill;
			width: 100%;
			height: 100%;
			object-fit: cover;
		}

		.caption {
			@include label;
			position: relative;
			@include glass;
			max-width: 100%;
			padding: 0.375rem 0.875rem;
			border-radius: 1rem;
			color: var(--ink);
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
			transition: background-color var(--fast) var(--ease-snap);
		}

		&:hover .caption {
			background: var(--pink);
			color: var(--night);
		}
	}

	.wall {
		display: grid;
		grid-template-columns: repeat(4, minmax(0, 1fr));
		gap: 1.5rem;

		@include below($bp-medium) {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}

		@include below($bp-narrow) {
			grid-template-columns: minmax(0, 1fr);
		}
	}

	// the tops are staggered; the last tile of each column stretches so the bottoms meet
	.column {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;

		> :last-child {
			flex: 1;
		}

		// the picture fills its tile whatever its size; the others centre what they show
		> :last-child:not(.picture) {
			grid-template-rows: 1fr auto;

			> :first-child {
				align-self: center;
			}
		}

		@include below($bp-narrow) {
			margin-top: 0 !important;
		}

		&:nth-child(2) {
			margin-top: 4rem;
		}

		&:nth-child(4) {
			margin-top: 2rem;
		}
	}

	.tile {
		position: relative;
		display: grid;
		align-content: end;
		gap: 0.5rem;
		min-height: 14rem;
		margin: 0;
		padding: 1.25rem;
		border: var(--hairline) solid var(--line);
		border-radius: 1.5rem;
		background: var(--surface);
		overflow: hidden;

		figcaption {
			@include label;
			position: relative;
			color: var(--soft);
		}

		&.picture {
			min-height: 16rem;
			border: none;

			img {
				@include fill;
				width: 100%;
				height: 100%;
				object-fit: cover;
			}

			figcaption {
				justify-self: start;
				@include glass;
				padding: 0.25rem 0.75rem;
				border-radius: 1rem;
				color: var(--ink);
			}
		}

		&.roll {
			min-height: 16rem;
			background: var(--lav);
			border: none;

			figcaption {
				color: var(--night);
			}
		}

		&.edit {
			min-height: 20rem;
			background: var(--blue);
			border: none;

			figcaption {
				color: var(--night);
			}
		}

		&.counter {
			gap: 1.25rem;
			min-height: 0;
			padding: 2rem;
			border: none;
			background: var(--night);

			figcaption {
				color: var(--lav);
			}
		}

		&.bots {
			min-height: 12rem;

			ul {
				display: grid;
				gap: 0.875rem;
				margin-bottom: 0.5rem;
			}

			li {
				display: flex;
				align-items: center;
				gap: 0.625rem;
				min-width: 0;
				font-family: var(--mono);
				font-size: clamp(0.75rem, 1.05vw, 1rem);
				white-space: nowrap;
			}
		}
	}

	.keys {
		display: flex;
		gap: 0.75rem;
		margin-bottom: 1rem;

		kbd {
			display: grid;
			place-items: center;
			flex: 1;
			max-width: 7rem;
			aspect-ratio: 1;
			border-radius: 1.25rem;
			background: var(--pink);
			box-shadow: 0 0.375rem 0 var(--purple);
			color: var(--night);
			font-family: var(--mono);
			font-size: 2.25rem;
			font-weight: 500;

			&:last-child {
				background: var(--blue);
			}
		}
	}

	.frame {
		--scale: 1;
		position: relative;
		width: 100%;
		border-radius: 0.75rem;
		overflow: hidden;

		// the counter keeps the pixel size it was designed at; the frame scales it
		iframe {
			// a frame under the pointer would take the wheel for itself and stop the page from scrolling
			pointer-events: none;
			position: absolute;
			top: 0;
			left: 0;
			border: none;
			transform: scale(var(--scale));
			transform-origin: 0 0;
		}
	}

	.online {
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 50%;
		background: #3ecf6e;
	}

	.playhead {
		position: absolute;
		top: -0.5rem;
		bottom: -0.5rem;
		left: 42%;
		width: 0.125rem;
		background: var(--night);
	}

	.notes {
		position: relative;
		display: grid;
		grid-template-columns: repeat(16, 1fr);
		grid-template-rows: repeat(7, 0.75rem);
		gap: 0.25rem;
		margin-bottom: 1rem;

		i {
			border-radius: 0.25rem;
			background: var(--night);
		}
	}

	.clips {
		position: relative;
		display: grid;
		grid-template-columns: repeat(12, 1fr);
		grid-template-rows: repeat(3, 2.5rem);
		gap: 0.375rem;
		margin-bottom: 1rem;

		i {
			border-radius: 0.375rem;
			background: var(--purple);
		}

		.track-2 {
			background: var(--pink);
		}

		.track-3 {
			background: var(--paper);
		}

	}
</style>
