<!-- Copyright (c) 2026 Belikhun. Licensed under the MIT License.
     See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { picture, WORKS, type WorkKind } from '#lib/content/site.ts';
	import { DESKTOP_MOTION, gsap, type Span } from '#lib/motion/gsap.ts';
	import { scrollToPosition } from '#lib/motion/stage.ts';

	import ArenaGame from './work/ArenaGame.svelte';
	import BlinkRequest from './work/BlinkRequest.svelte';
	import CloverCompile from './work/CloverCompile.svelte';
	import CtmsMock from './work/CtmsMock.svelte';
	import DealHunterMock from './work/DealHunterMock.svelte';
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

	/** Where in a card's unit of scroll the next card starts to slide over it; before that the finished visual rests. */
	const HANDOVER_AT = 0.65;

	/** How a card changes for each place it sits further down the pile: its scale, and its lift in rem. */
	const PILE_SHRINK = 0.03;
	const PILE_LIFT = 0.55;

	/** How much light a card loses for each place down the pile, and the least it is left with. */
	const PILE_DIM = 0.012;
	const PILE_DIMMEST = 0.94;

	/** The mark shown beside a card's name; `round` clips a square picture to a disc. */
	const ICONS: Partial<Record<WorkKind, { src: string; round?: boolean }>> = {
		luna: { src: picture('luna/icon.webp', '').src, round: true },
		harbor: { src: '/img/harbor/harbor-mark.svg' },
		vloom: { src: '/img/vloom/vloom-symbol.svg' },
		clover: { src: '/img/clover/clover-symbol.svg' },
		themis: { src: '/img/themis/themis-mark.svg' },
		hunter: { src: picture('hunter/icon.webp', '').src },
		ctms: { src: '/img/ctms/ctms-mark.svg' }
	};

	let root = $state<HTMLElement>();
	let visuals = $state<(Visual | undefined)[]>([]);
	let active = $state(0);
	let jump = $state<(index: number) => void>();

	/** How bright a card is drawn when it lies `depth` places down the pile. */
	function dimmed(depth: number): number {
		return Math.max(PILE_DIMMEST, 1 - depth * PILE_DIM);
	}

	function pad(value: number): string {
		return String(value).padStart(2, '0');
	}

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(DESKTOP_MOTION, () => {
				const cards = gsap.utils.toArray<HTMLElement>('.card');

				const length = cards.length - 0.25;
				const fills = gsap.utils.toArray<HTMLElement>('.segment i');

				// each card's share of the timeline: from halfway through its slide in to halfway through the next one's
				const shares = cards.map((_, index) => ({
					from: Math.max(index - 0.175, 0),
					to: index === cards.length - 1 ? length : index + 0.825
				}));

				const timeline = gsap.timeline({
					onUpdate: () => {
						const time = timeline.time();

						active = Math.min(cards.length - 1, Math.floor(time + 0.175));

						fills.forEach((fill, index) => {
							const share = shares[index]!;

							gsap.set(fill, { scaleX: gsap.utils.clamp(0, 1, (time - share.from) / (share.to - share.from)) });
						});
					},
					scrollTrigger: {
						trigger: root,
						pin: '.pin',
						start: 'top top',
						end: `+=${cards.length * SCROLL_PER_CARD}%`,
						scrub: 0.6
					}
				});

				// Each card owns one unit: it shows its visual over the first half, rests
				// finished for a moment, and the next card slides onto the pile at the end. It is on screen
				// for longer than that, from sliding in until the next card has covered
				// it, and its visual keeps something moving for that whole stretch.
				cards.forEach((card, index) => {
					visuals[index]?.animate(timeline, index, { from: Math.max(index - 0.5, 0), to: Math.min(index + 1.5, length) });

					const next = cards[index + 1];

					if (!next) {
						return;
					}

					timeline.fromTo(next, { yPercent: 115 }, { yPercent: 0, duration: 1 - HANDOVER_AT, ease: 'power2.out' }, index + HANDOVER_AT);

					// Nothing leaves the pile: as a card lands, every card under it steps one place
					// further back, a little smaller, a little higher and a little dimmer, so the
					// top edges of all the cards read so far stay in sight. They stay opaque: seen
					// through each other, their text and pictures would show as ghosts.
					for (let under = index; under >= 0; under--) {
						const depth = index + 1 - under;

						timeline
							.to(
								cards[under]!,
								{
									scale: 1 - depth * PILE_SHRINK,
									y: `${depth * -PILE_LIFT}rem`,
									duration: 1 - HANDOVER_AT,
									ease: 'none'
								},
								index + HANDOVER_AT
							)
							// both ends are spelled out: from no filter at all, the dimming would begin at black
							.fromTo(
								cards[under]!,
								{ filter: `brightness(${dimmed(depth - 1)})` },
								{ filter: `brightness(${dimmed(depth)})`, duration: 1 - HANDOVER_AT, ease: 'none', immediateRender: false },
								index + HANDOVER_AT
							);
					}
				});

				timeline.to({}, { duration: 0.25 }, length - 0.25);

				jump = (index) => {
					const trigger = timeline.scrollTrigger!;

					scrollToPosition(trigger.start + ((index + 0.3) / timeline.duration()) * (trigger.end - trigger.start));
				};

				return () => {
					jump = undefined;
				};
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
					{#if work.links}
						<p class="links">
							{#each work.links as link (link.href)}
								<a class="link" href={link.href} target="_blank" rel="noreferrer">{link.text} ↗</a>
							{/each}
						</p>
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
					{:else if work.kind === 'hunter'}
						<DealHunterMock bind:this={visuals[index]} />
					{:else if work.kind === 'ctms'}
						<CtmsMock bind:this={visuals[index]} />
					{/if}
				</div>
			</article>
		{/each}

		<nav class="rail" aria-label="selected work">
			{#each WORKS as work, index (work.name)}
				<button class="segment" class:active={index === active} type="button" onclick={() => jump?.(index)}>
					<span class="bar"><i></i></span>
					<span class="name">{pad(index + 1)} <span class="title">{work.short ?? work.name}</span></span>
				</button>
			{/each}
		</nav>
	</div>
</section>

<style lang="scss">
	// the stage ends on rounded corners, so the next scene does not meet it on a flat seam
	.work {
		border-radius: 0 0 2.5rem 2.5rem;
		background: var(--stage);
		overflow: clip;
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

		// on a phone the card's own padding gives way, so the visual gets the width
		@include below($bp-narrow) {
			gap: 1.5rem;
			padding: 1rem;
		}
		border-radius: var(--radius-card);
		background: var(--surface);

		@include stage {
			position: absolute;
			inset: 5.5rem clamp(1rem, 5vw, 5rem) 4.75rem;
			grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
			gap: 3rem;
			padding: 3rem;
			transform-origin: 50% 0%;
			// a short, light shadow: a long one would pile up over the cards beneath and turn them grey
			box-shadow: 0 0 0 var(--hairline) var(--card-edge), 0 -0.25rem 0.75rem rgba(42, 36, 64, 0.07);
		}
	}

	// one segment per card along the bottom of the deck: it fills as the card is read, and a click goes to it
	.rail {
		display: none;

		@include stage {
			// a strip of the stage itself, so cards sliding in pass behind it
			position: absolute;
			left: 0;
			right: 0;
			bottom: 0;
			z-index: 1;
			display: flex;
			gap: 0.75rem;
			// the fade at its top stays in the gap under the resting card, and never reaches the card itself
			padding: 1.5rem clamp(1rem, 5vw, 5rem) 1rem;
			background: linear-gradient(transparent, var(--stage) 1rem);
			pointer-events: none;
		}
	}

	.segment {
		@include bare-button;
		display: grid;
		flex: 1 1 0;
		gap: 0.375rem;
		min-width: 0;
		color: var(--ink);
		text-align: left;
		pointer-events: auto;
		opacity: 0.45;
		transition: flex-grow 0.6s var(--ease-out), opacity var(--fast) var(--ease-snap);

		&:hover {
			opacity: 0.8;
		}

		&.active {
			flex-grow: 3;
			opacity: 1;
		}
	}

	.bar {
		display: block;
		height: 0.25rem;
		border-radius: 1rem;
		background: color-mix(in srgb, var(--ink) 18%, transparent);
		overflow: hidden;

		i {
			display: block;
			height: 100%;
			border-radius: inherit;
			background: var(--ink);
			transform: scaleX(0);
			transform-origin: 0 50%;
		}
	}

	.name {
		@include label;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	// where the segments are too narrow for names, only the card being read keeps its name
	.title {
		@media (max-width: 100rem) {
			.segment:not(.active) & {
				display: none;
			}
		}
	}

	.text {
		display: grid;
		align-content: center;
		justify-items: start;
		gap: 1.25rem;
		min-width: 0;

		// the same frame on every card: the meta line along the top, the links along the
		// bottom, and the title block centred in what is left between them
		@include stage {
			grid-template-rows: auto 1fr auto auto 1fr;
			align-content: stretch;

			h3,
			.links {
				align-self: end;
			}
		}
	}

	.meta {
		@include label;
		color: var(--soft);
	}

	h3 {
		@include display;
		display: flex;
		align-items: flex-start;
		gap: 1rem;
		font-size: clamp(3rem, 6vw, 6rem);

		&.long {
			font-size: clamp(2.5rem, 4.2vw, 4.25rem);
		}
	}

	.icon {
		flex: none;
		width: 0.9em;
		height: 0.9em;
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
		color: var(--accent-text);
	}

	.links {
		display: flex;
		flex-wrap: wrap;
		gap: 0.375rem;
	}

	.link {
		padding: 0.5rem 0.875rem;
		white-space: nowrap;
		border-radius: 2rem;
		background: var(--ink);
		color: var(--bg);
		font-size: 0.875rem;
		font-weight: 500;
		transition: background-color var(--fast) var(--ease-snap), translate var(--fast) var(--ease-snap);

		&:hover {
			background: var(--purple);
			translate: 0 -0.125rem;
		}
	}

	.visual {
		min-width: 0;
		min-height: 20rem;
	}
</style>
