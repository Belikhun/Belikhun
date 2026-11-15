<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { MARQUEE } from '#lib/content/site.ts';
	import { gsap, MOTION, POINTER_MOTION, ScrollTrigger, SplitText } from '#lib/motion/gsap.ts';
	import { lastPointer, type Point } from '#lib/motion/pointer.ts';
	import { introReady } from '#lib/motion/stage.ts';

	import Avatar from './Avatar.svelte';
	import Emoji from './Emoji.svelte';

	/** Shards float at different depths; a larger depth moves further with the pointer. */
	const SHARDS = [
		{ left: 12, top: 30, size: 2.5, turn: 24, depth: 2.4, tone: 'pink' },
		{ left: 22, top: 66, size: 1.5, turn: -18, depth: 1.2, tone: 'blue' },
		{ left: 31, top: 72, size: 1.25, turn: 40, depth: 0.8, tone: 'purple' },
		{ left: 70, top: 70, size: 2, turn: -30, depth: 1.8, tone: 'blue' },
		{ left: 79, top: 58, size: 3, turn: 14, depth: 2.8, tone: 'pink' },
		{ left: 88, top: 28, size: 1.5, turn: 60, depth: 1.4, tone: 'purple' },
		{ left: 60, top: 78, size: 1.25, turn: -50, depth: 1, tone: 'blue' }
	];

	const POINTER_REACH = 1.25;

	/** Enough copies of the phrases that half the track is wider than any screen; must stay even for the loop. */
	const MARQUEE_COPIES = Array.from({ length: 12 }, (_, index) => index);

	/** Seconds for one copy to pass. */
	const MARQUEE_PACE = 14;

	/** The furthest the marquee leans while the page is scrolled fast, in degrees. */
	const MARQUEE_LEAN = 14;

	let root = $state<HTMLElement>();

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(MOTION, () => {
				const split = SplitText.create('.wordmark', { type: 'chars', mask: 'chars' });

				// The avatar and the shards also follow the pointer. A `from` tween would put back the position
				// they had when it was made as it starts, dropping what the pointer has given them since; so
				// they are hidden here and brought in with `to`, which leaves their x and y alone.
				gsap.set('.avatar', { yPercent: 12, scale: 0.92, autoAlpha: 0 });
				gsap.set('.shard', { scale: 0, autoAlpha: 0 });

				const intro = gsap.timeline({ paused: true })
					.from(split.chars, { yPercent: 115, duration: 0.9, stagger: 0.045, ease: 'power4.out' })
					.to('.avatar', { yPercent: 0, scale: 1, autoAlpha: 1, duration: 1.2, ease: 'power3.out' }, 0.25)
					.from('.marquee', { yPercent: 100, duration: 0.7, ease: 'power3.out' }, 0.4)
					.to('.shard', { scale: 1, autoAlpha: 1, duration: 0.6, stagger: 0.05, ease: 'back.out(2)' }, 0.5)
					.from('.chip', { autoAlpha: 0, y: '1rem', duration: 0.5, stagger: 0.1 }, 0.7);

				introReady().then(() => intro.play());

				gsap.to('.avatar .figure', { y: '-1rem', duration: 3.2, ease: 'sine.inOut', yoyo: true, repeat: -1 });

				gsap.utils.toArray<HTMLElement>('.shard i').forEach((shard, index) => {
					gsap.to(shard, {
						y: `${index % 2 === 0 ? -0.75 : 0.75}rem`,
						rotation: index % 2 === 0 ? 8 : -8,
						duration: 2.4 + index * 0.35,
						ease: 'sine.inOut',
						yoyo: true,
						repeat: -1
					});
				});

				gsap.timeline({
					scrollTrigger: { trigger: root, start: 'top top', end: 'bottom top', scrub: 0.6 }
				})
					.to('.wordmark-drift', { yPercent: -45, ease: 'none' }, 0)
					.to('.card', { scale: 0.92, borderRadius: '4rem', ease: 'none' }, 0)
					.to('.avatar-drift', { yPercent: 8, ease: 'none' }, 0);

				const loop = gsap.to('.track', {
					xPercent: -50,
					duration: (MARQUEE_COPIES.length / 2) * MARQUEE_PACE,
					ease: 'none',
					repeat: -1
				});
				const lean = gsap.quickTo('.track', 'skewX', { duration: 0.5, ease: 'power3.out' });
				let settle: gsap.core.Tween | undefined;

				ScrollTrigger.create({
					start: 0,
					end: 'max',
					onUpdate: (self) => {
						settle?.kill();
						loop.timeScale(1 + Math.min(Math.abs(self.getVelocity()) / 400, 6));
						settle = gsap.to(loop, { timeScale: 1, duration: 1.2, ease: 'power2.out', onStart: () => lean(0) });

						// the words lean into the scroll, like a flag in the wind of it
						lean(gsap.utils.clamp(-MARQUEE_LEAN, MARQUEE_LEAN, self.getVelocity() / -250));
					}
				});
			});

			media.add(POINTER_MOTION, () => {
				const layers = gsap.utils.toArray<HTMLElement>('[data-depth]').map((layer) => ({
					node: layer,
					depth: Number(layer.dataset.depth),
					x: gsap.quickTo(layer, 'x', { duration: 0.9, ease: 'power3.out' }),
					y: gsap.quickTo(layer, 'y', { duration: 0.9, ease: 'power3.out' })
				}));

				const offset = (point: Point): Point => {
					const rem = parseFloat(getComputedStyle(document.documentElement).fontSize);

					return {
						x: (point.x / window.innerWidth - 0.5) * POINTER_REACH * rem,
						y: (point.y / window.innerHeight - 0.5) * POINTER_REACH * rem
					};
				};

				const follow = (event: PointerEvent): void => {
					const { x, y } = offset({ x: event.clientX, y: event.clientY });

					for (const layer of layers) {
						layer.x(x * layer.depth);
						layer.y(y * layer.depth);
					}
				};

				// the layers start where the pointer already is, so nothing swings into place while the hero is still arriving
				const known = lastPointer();

				if (known) {
					const { x, y } = offset(known);

					for (const layer of layers) {
						gsap.set(layer.node, { x: x * layer.depth, y: y * layer.depth });
					}
				}

				window.addEventListener('pointermove', follow);

				return () => window.removeEventListener('pointermove', follow);
			});
		}, root);

		return () => context.revert();
	});
</script>

<section class="hero" id="top" bind:this={root}>
	<div class="card">
		<div class="wordmark-drift">
			<div data-depth="-0.6">
				<h1 class="wordmark">belikhun</h1>
			</div>
		</div>

		{#each SHARDS as shard, index (index)}
			<span
				class="shard {shard.tone}"
				data-depth={shard.depth}
				style:left="{shard.left}%"
				style:top="{shard.top}%"
				style:--size="{shard.size}rem"
				style:--turn="{shard.turn}deg"
			>
				<i></i>
			</span>
		{/each}

		<div class="avatar-drift">
			<div class="avatar" data-depth="1">
				<Avatar />
			</div>
		</div>

		<p class="chip years"><strong>9 yrs</strong> of building things <Emoji code="1f680" char="🚀" /></p>
		<a class="chip scroll" href="#about">scroll ↓</a>
	</div>

	<div class="marquee" aria-label={MARQUEE.map((phrase) => phrase.text).join(', ')}>
		<div class="track" aria-hidden="true">
			{#each MARQUEE_COPIES as copy (copy)}
				{#each MARQUEE as phrase, index (phrase.text)}
					<span class="phrase" class:outlined={index % 2 === 1}>{phrase.text}</span>
					{#if phrase.emoji}
						<span class="badge" class:blue={index % 2 === 1}><Emoji code={phrase.emoji.code} char={phrase.emoji.char} /></span>
					{/if}
					<svg class="star" viewBox="0 0 100 100"><path d="M50 0C54 34 66 46 100 50C66 54 54 66 50 100C46 66 34 54 0 50C34 46 46 34 50 0Z" /></svg>
				{/each}
			{/each}
		</div>
	</div>
</section>

<style lang="scss">
	.hero {
		display: flex;
		flex-direction: column;
		height: 100svh;
		min-height: 36rem;
		padding: 0.75rem 0.75rem 0;
	}

	.card {
		position: relative;
		flex: 1;
		min-height: 0;
		border-radius: 2rem;
		background: var(--sky);
		overflow: hidden;
		transform-origin: 50% 0%;
	}

	.wordmark-drift {
		position: absolute;
		top: 11%;
		left: 0;
		right: 0;
		text-align: center;
	}

	.wordmark {
		@include display;
		font-size: clamp(4.5rem, 21vw, 24rem);
		color: var(--wordmark);
		white-space: nowrap;
	}

	.avatar-drift {
		position: absolute;
		left: 50%;
		bottom: -4%;
		height: 92%;
		aspect-ratio: 708 / 1200;
		// the standalone property, so GSAP's own transform never overwrites the centring
		translate: -50% 0;

		@include below($bp-narrow) {
			height: 68%;
		}
	}

	.avatar {
		height: 100%;
	}

	.shard {
		position: absolute;
		width: var(--size);

		i {
			display: block;
			aspect-ratio: 3 / 5;
			rotate: var(--turn);
			clip-path: polygon(30% 0, 100% 18%, 70% 100%, 0 82%);
			background: var(--pink);
		}

		&.blue i {
			background: var(--blue);
		}

		&.paper i {
			background: var(--paper);
		}

		&.purple i {
			background: var(--purple);
		}
	}

	.chip {
		position: absolute;
		bottom: 0;
		padding: 1rem 1.5rem;
		background: var(--bg);
		font-size: 0.875rem;
		line-height: 1.3;

		strong {
			@include display;
			display: block;
			font-size: 2rem;
			letter-spacing: -0.02em;
		}

		&.years {
			left: 0;
			border-top-right-radius: 1.5rem;
		}

		&.scroll {
			right: 0;
			border-top-left-radius: 1.5rem;
		}
	}

	.marquee {
		flex: none;
		margin: 0.75rem -0.75rem 0;
		padding: 0.75rem 0;
		background: var(--night);
		color: var(--paper);
		overflow: hidden;
	}

	.track {
		display: flex;
		align-items: center;
		width: max-content;
		white-space: nowrap;

		// a margin, not a gap: both copies must be exactly the same width for the loop to be seamless
		> * {
			flex: none;
			margin-right: clamp(1rem, 2vw, 2rem);
		}
	}

	// the phrases take turns: one solid, the next drawn in outline
	.phrase {
		@include display;
		font-size: clamp(2.25rem, 4.6vw, 4.5rem);
		line-height: 1.2;

		&.outlined {
			// filled with the band's own colour and painted over the stroke: the font's
			// overlapping contours would otherwise show as lines inside the letters
			color: var(--night);
			-webkit-text-stroke: 0.2rem var(--lav);
			paint-order: stroke fill;
		}
	}

	.badge {
		display: grid;
		place-items: center;
		padding: 0.25rem 1.25rem;
		border-radius: 3rem;
		background: var(--pink);
		font-size: clamp(1.5rem, 3vw, 3rem);
		line-height: 1;
		rotate: -6deg;

		&.blue {
			background: var(--blue);
			rotate: 6deg;
		}
	}

	.star {
		width: clamp(1.25rem, 2.4vw, 2.5rem);
		fill: var(--lav);

		@include motion {
			animation: turn 6s linear infinite;
		}
	}

	@keyframes turn {
		to {
			rotate: 360deg;
		}
	}
</style>
