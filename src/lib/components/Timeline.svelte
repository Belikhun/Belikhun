<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { STOPS } from '#lib/content/site.ts';
	import { DESKTOP_MOTION, gsap } from '#lib/motion/gsap.ts';

	import Emoji from './Emoji.svelte';

	const FIRST = STOPS[0]!.year;
	const LAST = STOPS[STOPS.length - 1]!.year;

	let root = $state<HTMLElement>();
	let active = $state(0);

	const year = $derived(STOPS[active]!.year);

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(DESKTOP_MOTION, () => {
				const track = root!.querySelector<HTMLElement>('.track')!;
				const distance = (): number => track.scrollWidth - window.innerWidth;

				gsap.to(track, {
					x: () => -distance(),
					ease: 'none',
					scrollTrigger: {
						trigger: root,
						pin: '.pin',
						start: 'top top',
						end: () => `+=${distance()}`,
						scrub: 0.6,
						invalidateOnRefresh: true,
						onUpdate: (self) => {
							active = Math.round(self.progress * (STOPS.length - 1));
						}
					}
				});

				// starts while the scene is still arriving, so the ribbon is always ahead of the cards
				gsap.fromTo(
					'.ribbon path',
					{ strokeDashoffset: 1 },
					{
						strokeDashoffset: 0,
						ease: 'none',
						scrollTrigger: {
							trigger: root,
							start: 'top 70%',
							end: () => `+=${distance() * 0.85 + window.innerHeight * 0.7}`,
							scrub: 0.6,
							invalidateOnRefresh: true
						}
					}
				);
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
				<svg viewBox="0 0 1000 100" preserveAspectRatio="none">
					<path
						pathLength="1"
						d="M0 60 C 60 10, 120 95, 190 50 S 310 10, 380 55 S 500 95, 570 45 S 690 5, 760 55 S 880 95, 1000 40"
					/>
				</svg>
			</li>
			{#each STOPS as stop, index (stop.year)}
				<li class="stop" class:active={index === active}>
					<span class="when">{stop.year}</span>
					<h3>{stop.title}</h3>
					<ul>
						{#each stop.lines as line (line)}
							<li>{line}</li>
						{/each}
					</ul>
				</li>
			{/each}
		</ol>

		<ol class="ruler" aria-hidden="true">
			{#each STOPS as stop, index (stop.year)}
				<li class:active={index === active}>{String(stop.year).slice(2)}</li>
			{/each}
		</ol>
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
			position: absolute;
			left: 3vw;
			bottom: 3rem;
			display: block;
			font-size: clamp(12rem, 26vw, 28rem);
			color: transparent;
			-webkit-text-stroke: 0.125rem var(--lav);
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
		border-left: 0.25rem solid var(--pink);
		margin-left: clamp(1rem, 5vw, 5rem);
		padding-left: 1.5rem;

		@include stage {
			display: flex;
			align-items: center;
			gap: 3rem;
			width: max-content;
			margin: 0;
			padding-inline: 14vw 30vw;
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
			position: absolute;
			top: 50%;
			left: 0;
			width: 100%;
			height: 12rem;
			margin-top: -6rem;
			overflow: visible;
		}

		path {
			fill: none;
			stroke: var(--pink);
			stroke-width: 0.75rem;
			stroke-linecap: round;
			stroke-dasharray: 1;
			vector-effect: non-scaling-stroke;
		}
	}

	.stop {
		position: relative;
		display: grid;
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
			font-size: 1.25rem;
			font-weight: 600;
			line-height: 1.3;
		}

		ul {
			display: grid;
			gap: 0.25rem;
			color: var(--soft);
		}
	}

	.when {
		@include label;
		color: var(--purple);
	}

	.ruler {
		display: none;

		@include stage {
			@include label;
			position: absolute;
			left: 0;
			right: 0;
			bottom: 2rem;
			display: flex;
			justify-content: space-between;
			padding-inline: clamp(1rem, 5vw, 5rem);
			color: var(--soft);
		}

		li {
			transition: color 0.3s;

			&.active {
				color: var(--ink);

				&::before {
					content: '● ';
				}
			}
		}
	}
</style>
