<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { picture, WORKS } from '#lib/content/site.ts';
	import { DESKTOP_MOTION, gsap } from '#lib/motion/gsap.ts';

	import ArenaCrowd from './work/ArenaCrowd.svelte';
	import CloverBuild from './work/CloverBuild.svelte';
	import CodeSample from './work/CodeSample.svelte';
	import FeatureList from './work/FeatureList.svelte';
	import HarborRoute from './work/HarborRoute.svelte';
	import LunaWall from './work/LunaWall.svelte';
	import Shots from './work/Shots.svelte';
	import VloomLayers from './work/VloomLayers.svelte';

	interface Visual {
		animate(timeline: gsap.core.Timeline, at: number): void;
	}

	/** How much scroll each card gets, as a share of the viewport height. */
	const SCROLL_PER_CARD = 66;

	const LUNA_ICON = picture('luna/icon.webp', '');

	const MANULIFE_FEATURES = ['agent onboarding paths', 'exams and certificates', 'team dashboards'];

	const BLINK_LINES = [
		'// routes/web.php',
		'use Blink\\Http\\Router;',
		'',
		'Router::GET("/", fn () => "hello");',
		'',
		'Router::GET("/user/{id}", function (int $id) {',
		'	return App\\Model\\User::getByID($id, Blink\\Model::MUST_EXIST);',
		'});'
	];

	const THEMIS_SHOTS = [
		picture('themis/light.webp', 'the contest ranking in the day theme'),
		picture('themis/dark.webp', 'the contest ranking in the night theme'),
		picture('themis/overview.webp', 'submitting a solution with the timer running')
	];

	const CTMS_SHOTS = [
		picture('ctms/schedule.webp', 'the class schedule on desktop'),
		picture('ctms/phone-schedule.webp', 'the class schedule on a phone'),
		picture('ctms/phone-register.webp', 'class registration on a phone')
	];

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

				// Each card owns one unit: it shows its visual over the first half,
				// and the next card slides over it during the second.
				cards.forEach((card, index) => {
					visuals[index]?.animate(timeline, index);

					const next = cards[index + 1];

					if (!next) {
						return;
					}

					timeline
						.fromTo(next, { yPercent: 115 }, { yPercent: 0, duration: 0.5, ease: 'power2.out' }, index + 0.5)
						.to(card, { scale: 0.94, yPercent: -3, duration: 0.5, ease: 'none' }, index + 0.5)
						.set(card, { autoAlpha: 0 }, index + 1.5);
				});

				timeline.to({}, { duration: 0.25 });
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
						{#if work.kind === 'luna'}
							<img class="icon" src={LUNA_ICON.src} width={LUNA_ICON.width} height={LUNA_ICON.height} alt="" />
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
						<HarborRoute bind:this={visuals[index]} />
					{:else if work.kind === 'vloom'}
						<VloomLayers bind:this={visuals[index]} />
					{:else if work.kind === 'clover'}
						<CloverBuild bind:this={visuals[index]} />
					{:else if work.kind === 'arena'}
						<ArenaCrowd bind:this={visuals[index]} />
					{:else if work.kind === 'manulife'}
						<FeatureList bind:this={visuals[index]} title="what it covers" features={MANULIFE_FEATURES} />
					{:else if work.kind === 'blink'}
						<CodeSample bind:this={visuals[index]} file="a working site" lines={BLINK_LINES} />
					{:else if work.kind === 'themis'}
						<Shots bind:this={visuals[index]} pictures={THEMIS_SHOTS} />
					{:else if work.kind === 'ctms'}
						<Shots bind:this={visuals[index]} pictures={CTMS_SHOTS} tone="blue" />
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
		border-radius: 50%;
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
