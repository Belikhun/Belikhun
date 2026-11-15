<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { picture } from '#lib/content/site.ts';
	import { DESKTOP_MOTION, gsap, MOTION } from '#lib/motion/gsap.ts';

	const LANTERN = picture('luna/wall/lantern.webp', 'a lantern over Luna\'s survival world');
	const RACING = picture('luna/wall/boat-racing.webp', 'the boat racing event on Luna');

	const PEAK_PP = 727;

	/** Piano roll notes: column, row and length on a 16 by 7 grid. */
	const NOTES = [
		[1, 5, 2], [3, 4, 1], [4, 3, 3], [7, 5, 1], [8, 2, 2], [10, 4, 2], [12, 1, 3], [13, 6, 2],
		[2, 7, 1], [6, 6, 2], [9, 7, 1], [15, 3, 2]
	];

	/** Video timeline clips: track, start and length on a 12-column grid. */
	const CLIPS = [
		[1, 1, 4], [1, 5, 3], [1, 9, 4], [2, 2, 6], [2, 9, 3], [3, 1, 2], [3, 4, 5], [3, 10, 2]
	];

	/** Unstable-rate hits, as offsets from the centre of the bar in percent. */
	const HITS = [-34, -21, -12, -8, -3, 2, 4, 9, 14, 19, 27, 38, -5, 6, -16];

	let root = $state<HTMLElement>();
	let pp = $state(PEAK_PP);

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(MOTION, () => {
				const counter = { value: 0 };

				gsap.to(counter, {
					value: PEAK_PP,
					duration: 7,
					ease: 'power1.out',
					repeat: -1,
					repeatDelay: 2.5,
					scrollTrigger: { trigger: root, start: 'top bottom', end: 'bottom top', toggleActions: 'play pause resume pause' },
					onUpdate: () => {
						pp = Math.round(counter.value);
					}
				});

				gsap.from('.tile', {
					scale: 0.9,
					autoAlpha: 0,
					duration: 0.7,
					ease: 'power3.out',
					stagger: 0.06,
					scrollTrigger: { trigger: '.wall', start: 'top 85%' }
				});

				gsap.to('.hit', {
					x: 'random(-0.5, 0.5)rem',
					duration: 0.4,
					ease: 'sine.inOut',
					repeat: -1,
					yoyo: true,
					stagger: { each: 0.07, from: 'random' }
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

<section class="off" id="off-hours" bind:this={root}>
	<header>
		<h2>off-hours</h2>
		<p>when i'm not shipping i'm clicking circles, making noise in FL Studio, cutting videos, or running a Minecraft network for friends.</p>
	</header>

	<div class="wall">
		<div class="column">
			<figure class="tile dark">
				<p class="pp">{pp}<small>pp</small></p>
				<p class="stats">98.42% · 1,204x</p>
				<figcaption>osu! · pp counter</figcaption>
			</figure>
			<figure class="tile keypad">
				<div class="keys" aria-hidden="true">
					<kbd>z</kbd>
					<kbd>x</kbd>
				</div>
				<figcaption>arduino keypad</figcaption>
			</figure>
		</div>

		<div class="column">
			<figure class="tile roll">
				<div class="notes" aria-hidden="true">
					{#each NOTES as [column, row, length], index (index)}
						<i style:grid-column="{column} / span {length}" style:grid-row={row}></i>
					{/each}
				</div>
				<figcaption>FL Studio</figcaption>
			</figure>
			<figure class="tile picture">
				<img src={LANTERN.src} width={LANTERN.width} height={LANTERN.height} alt={LANTERN.alt} loading="lazy" />
				<figcaption>Luna</figcaption>
			</figure>
		</div>

		<div class="column">
			<figure class="tile edit">
				<div class="clips" aria-hidden="true">
					{#each CLIPS as [track, start, length], index (index)}
						<i class="track-{track}" style:grid-row={track} style:grid-column="{start} / span {length}"></i>
					{/each}
					<b></b>
				</div>
				<figcaption>video edits</figcaption>
			</figure>
			<figure class="tile card">
				<span class="clip" aria-hidden="true">✕</span>
				<p><strong>belikhun</strong>osu! player</p>
				<figcaption>user card</figcaption>
			</figure>
		</div>

		<div class="column">
			<figure class="tile rate">
				<div class="bar" aria-hidden="true">
					{#each HITS as hit, index (index)}
						<i class="hit" style:left="{50 + hit}%"></i>
					{/each}
				</div>
				<figcaption>osu! · unstable rate</figcaption>
			</figure>
			<figure class="tile picture">
				<img src={RACING.src} width={RACING.width} height={RACING.height} alt={RACING.alt} loading="lazy" />
				<figcaption>Minecraft plugins</figcaption>
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

		&.dark {
			min-height: 18rem;
			border: none;
			background: var(--night);
			color: var(--paper);
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

		&.card {
			grid-template-columns: auto 1fr;
			align-items: center;
			column-gap: 1rem;

			figcaption {
				grid-column: 1 / 3;
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

	.pp {
		@include display;
		font-size: clamp(2.5rem, 9vw, 4.5rem);
		color: var(--pink);
		font-variant-numeric: tabular-nums;

		small {
			margin-left: 0.25rem;
			font-size: 1.5rem;
		}
	}

	.stats {
		@include label;
		color: var(--blue);
	}

	.notes {
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

		// the playhead
		b {
			position: absolute;
			top: -0.5rem;
			bottom: -0.5rem;
			left: 42%;
			width: 0.125rem;
			background: var(--night);
		}
	}

	.clip {
		display: grid;
		place-items: center;
		width: 3.5rem;
		height: 3.5rem;
		border-radius: 50%;
		background: var(--lav);
		color: var(--night);
		font-size: 1.5rem;
		font-weight: 600;
	}

	.card p {
		display: grid;
		color: var(--soft);

		strong {
			color: var(--ink);
			font-size: 1.25rem;
			font-weight: 600;
		}
	}

	.bar {
		position: relative;
		height: 2.5rem;
		margin-bottom: 1rem;
		border-radius: 0.5rem;
		background: linear-gradient(90deg, var(--pink), var(--blue) 35%, var(--blue) 65%, var(--pink));

		&::after {
			content: '';
			position: absolute;
			top: -0.5rem;
			bottom: -0.5rem;
			left: 50%;
			width: 0.125rem;
			background: var(--ink);
		}
	}

	.hit {
		position: absolute;
		top: 0.375rem;
		bottom: 0.375rem;
		width: 0.125rem;
		background: var(--night);
		opacity: 0.6;
	}
</style>
