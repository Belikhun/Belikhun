<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { picture, WORKS, type WorkKind } from '#lib/content/site.ts';
	import { DESKTOP_MOTION, gsap, type Span } from '#lib/motion/gsap.ts';

	import ArenaGame from './work/ArenaGame.svelte';
	import BlinkRequest from './work/BlinkRequest.svelte';
	import CloverCompile from './work/CloverCompile.svelte';
	import CtmsMock from './work/CtmsMock.svelte';
	import HarborConsole from './work/HarborConsole.svelte';
	import HomeAssistant from './work/HomeAssistant.svelte';
	import LunaWall from './work/LunaWall.svelte';
	import ThemisMock from './work/ThemisMock.svelte';
	import VloomStack from './work/VloomStack.svelte';

	interface Visual {
		animate(timeline: gsap.core.Timeline, at: number, shown: Span): void;
	}

	/** How much scroll each card gets, as a share of the viewport height. */
	const SCROLL_PER_CARD = 66;

	/** The mark shown beside a card's name; `round` clips a square picture to a disc. */
	const ICONS: Partial<Record<WorkKind, { src: string; round?: boolean }>> = {
		luna: { src: picture('luna/icon.webp', '').src, round: true },
		harbor: { src: '/img/harbor/harbor-mark.svg' },
		vloom: { src: '/img/vloom/vloom-symbol.svg' },
		clover: { src: '/img/clover/clover-symbol.svg' },
		themis: { src: '/img/themis/themis-mark.svg' },
		ctms: { src: '/img/ctms/ctms-mark.svg' }
	};

	let root = $state<HTMLElement>();
	let visuals = $state<(Visual | undefined)[]>([]);

	function pad(value: number): string {
		return String(value).padStart(2, '0');
	}

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(DESKTOP_MOTION, () => {
				const cards = gsap.utils.toArray<HTMLElement>('.card');

				const timeline = gsap.timeline({
					scrollTrigger: {
						trigger: root,
						pin: '.pin',
						start: 'top top',
						end: `+=${cards.length * SCROLL_PER_CARD}%`,
						scrub: 0.6
					}
				});

				const length = cards.length - 0.25;

				// Each card owns one unit: it shows its visual over the first half,
				// and the next card slides over it during the second. It is on screen
				// for longer than that, from sliding in until the next card has covered
				// it, and its visual keeps something moving for that whole stretch.
				cards.forEach((card, index) => {
					visuals[index]?.animate(timeline, index, { from: Math.max(index - 0.5, 0), to: Math.min(index + 1.5, length) });

					const next = cards[index + 1];

					if (!next) {
						return;
					}

					timeline
						.fromTo(next, { yPercent: 115 }, { yPercent: 0, duration: 0.5, ease: 'power2.out' }, index + 0.5)
						.to(card, { scale: 0.94, yPercent: -3, duration: 0.5, ease: 'none' }, index + 0.5)
						.set(card, { autoAlpha: 0 }, index + 1.5);
				});

				timeline.to({}, { duration: 0.25 }, length - 0.25);
			});
		}, root);

		return () => context.revert();
	});
</script>

<section class="work" id="work" bind:this={root}>
	<div class="pin">
		{#each WORKS as work, index (work.name)}
			<article class="card">
				<div class="text">
					<p class="meta">{pad(index + 1)} / {pad(WORKS.length)} · {work.context} · {work.years}</p>
					<h3 class:long={work.name.length > 12}>
						{#if ICONS[work.kind]}
							<img class="icon" class:round={ICONS[work.kind]?.round} src={ICONS[work.kind]?.src} width="256" height="256" alt="" />
						{/if}
						{work.name}
					</h3>
					<p class="body">{work.body}</p>
					<p class="role">{work.role}</p>
					{#if work.link}
						<a class="link" href={work.link} target="_blank" rel="noreferrer">source ↗</a>
					{/if}
				</div>

				<div class="visual">
					{#if work.kind === 'luna'}
						<LunaWall bind:this={visuals[index]} />
					{:else if work.kind === 'harbor'}
						<HarborConsole bind:this={visuals[index]} />
					{:else if work.kind === 'vloom'}
						<VloomStack bind:this={visuals[index]} />
					{:else if work.kind === 'clover'}
						<CloverCompile bind:this={visuals[index]} />
					{:else if work.kind === 'arena'}
						<ArenaGame bind:this={visuals[index]} />
					{:else if work.kind === 'blink'}
						<BlinkRequest bind:this={visuals[index]} />
					{:else if work.kind === 'home'}
						<HomeAssistant bind:this={visuals[index]} />
					{:else if work.kind === 'themis'}
						<ThemisMock bind:this={visuals[index]} />
					{:else if work.kind === 'ctms'}
						<CtmsMock bind:this={visuals[index]} />
					{/if}
				</div>
			</article>
		{/each}
	</div>
</section>

<style lang="scss">
	.work {
		background: var(--stage);
	}

	.pin {
		@include gutter;
		display: grid;
		gap: 1.5rem;
		padding-block: 3rem;

		@include stage {
			position: relative;
			display: block;
			height: 100vh;
			padding-block: 0;
			overflow: hidden;
		}
	}

	.card {
		display: grid;
		gap: 2rem;
		padding: 1.5rem;
		border-radius: var(--radius-card);
		background: var(--surface);

		@include stage {
			position: absolute;
			inset: 5.5rem clamp(1rem, 5vw, 5rem) 2.5rem;
			grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
			gap: 3rem;
			padding: 3rem;
			transform-origin: 50% 0%;
			box-shadow: 0 -1rem 3rem rgba(42, 36, 64, 0.12);
		}
	}

	.text {
		display: grid;
		align-content: center;
		justify-items: start;
		gap: 1.25rem;
		min-width: 0;
	}

	.meta {
		@include label;
		color: var(--soft);
	}

	h3 {
		@include display;
		display: flex;
		align-items: center;
		gap: 1rem;
		font-size: clamp(3rem, 6vw, 6rem);

		&.long {
			font-size: clamp(2.5rem, 4.2vw, 4.25rem);
		}
	}

	.icon {
		flex: none;
		width: 1em;
		height: 1em;
		object-fit: contain;

		&.round {
			border-radius: 50%;
		}
	}

	.body {
		max-width: 28rem;
		font-size: 1.25rem;
		line-height: 1.5;
	}

	.role {
		@include label;
		color: var(--purple);
	}

	.link {
		padding: 0.5rem 1.25rem;
		border-radius: 2rem;
		background: var(--ink);
		color: var(--bg);
		font-size: 0.875rem;
		font-weight: 500;
	}

	.visual {
		min-width: 0;
		min-height: 20rem;
	}
</style>
