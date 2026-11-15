<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { picture } from '#lib/content/site.ts';
	import { DESKTOP_MOTION, gsap, MOTION, ScrollTrigger } from '#lib/motion/gsap.ts';

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
	let live = $state(false);

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
					scale: 0.9,
					autoAlpha: 0,
					duration: 0.7,
					ease: 'power3.out',
					stagger: 0.06,
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

				// the loops only run while the section is on screen, and the counters load the first time it is
				ScrollTrigger.create({
					trigger: root,
					start: 'top bottom',
					end: 'bottom top',
					onToggle: (self) => {
						live ||= self.isActive;

						for (const loop of looping) {
							loop.paused(!self.isActive);
						}
					}
				});
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
		{#if live}
			<iframe src={frame.src} title={frame.title} width={frame.width} height={frame.height} loading="lazy"></iframe>
		{/if}
	</div>
{/snippet}

<section class="off" id="off-hours" bind:this={root}>
	<header>
		<h2>off-hours <Emoji code="1f47e" char="👾" /></h2>
		<p>when i'm not shipping i'm clicking circles and writing the counters that sit around them, making noise in FL Studio, cutting videos, or running a Minecraft network for friends.</p>
	</header>

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
				<img src={LANTERN.src} width={LANTERN.width} height={LANTERN.height} alt={LANTERN.alt} loading="lazy" />
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

	.wall {
		display: grid;
		grid-template-columns: repeat(4, minmax(0, 1fr));
		align-items: start;
		gap: 1.5rem;

		@include below($bp-medium) {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}

	.column {
		display: grid;
		gap: 1.5rem;

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
				padding: 0.25rem 0.75rem;
				border-radius: 1rem;
				background: var(--bg);
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
				gap: 0.5rem;
				margin-bottom: 0.5rem;
			}

			li {
				display: flex;
				align-items: center;
				gap: 0.625rem;
				font-family: var(--mono);
				font-size: 0.875rem;
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
			max-width: 4.5rem;
			aspect-ratio: 1;
			border-radius: 1rem;
			background: var(--pink);
			box-shadow: 0 0.375rem 0 var(--purple);
			color: var(--night);
			font-family: var(--mono);
			font-size: 1.5rem;
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
