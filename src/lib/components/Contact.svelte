<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { EMAIL, GITHUB, GPG_KEY_FILE, GPG_KEY_ID } from '#lib/content/site.ts';
	import { gsap, MOTION, POINTER_MOTION, SplitText } from '#lib/motion/gsap.ts';

	import Charm from './Charm.svelte';
	import Emoji from './Emoji.svelte';
	import KeyRain from './KeyRain.svelte';

	const COPIED_FOR_MS = 1800;
	const BURST = [0, 1, 2, 3, 4, 5];

	/** The cursors that put the ending together, named after what each one carries. */
	const HANDS = [
		{ name: 'layout', tone: 'pink' },
		{ name: 'mail', tone: 'blue' },
		{ name: 'github', tone: 'paper' }
	];

	const SCALLOPS = Array.from({ length: 48 }, (_, index) => index);

	interface Box {
		left: number;
		top: number;
		width: number;
		height: number;
	}

	let root = $state<HTMLElement>();
	let copied = $state(false);
	let badge = $state('');

	/** Where a part sits inside the card, in the card's own unscaled pixels. */
	function boxOf(card: HTMLElement, selector: string): Box {
		const frame = card.getBoundingClientRect();
		const part = card.querySelector(selector)!.getBoundingClientRect();
		const scale = frame.width / card.offsetWidth;

		return {
			left: (part.left - frame.left) / scale,
			top: (part.top - frame.top) / scale,
			width: part.width / scale,
			height: part.height / scale
		};
	}

	/**
	 * Three cursors assemble the ending and leave: one measures the words, the
	 * other two carry the buttons up into place.
	 */
	function assemble(card: HTMLElement): gsap.core.Timeline {
		const [layout, mail, github] = gsap.utils.toArray<HTMLElement>('.hand', card);
		const ghost = card.querySelector('.ghost')!;
		const buttons = [card.querySelector('.mail')!, card.querySelector('.github')!];

		gsap.set(buttons, { y: 0 });

		const words = boxOf(card, '.words');
		const pills = [boxOf(card, '.mail'), boxOf(card, '.github')];
		const drop = card.offsetHeight;
		const timeline = gsap.timeline();

		[mail!, github!].forEach((hand, index) => {
			const pill = pills[index]!;
			const rise = drop - pill.top + 40;
			const hold = { x: pill.left + pill.width * 0.7, y: pill.top + pill.height * 0.5 };
			const away = hold.x + (index === 0 ? -1 : 1) * card.offsetWidth * 0.6;

			timeline.add(
				gsap.timeline()
					.set(hand, { x: hold.x, y: hold.y + rise, autoAlpha: 1 })
					.fromTo(buttons[index]!, { y: rise }, { y: 0, duration: 1, ease: 'power3.out' })
					.to(hand, { y: hold.y, duration: 1, ease: 'power3.out' }, '<')
					.to(hand, { x: away, y: drop + 60, duration: 0.8, ease: 'power2.in' }, '>0.15')
					.set(hand, { autoAlpha: 0 }),
				0.9 + index * 0.18
			);
		});

		timeline.add(
			gsap.timeline()
				.set(layout!, { x: -60, y: words.top, autoAlpha: 1 })
				.to(layout!, { x: words.left, y: words.top, duration: 0.6, ease: 'power2.inOut' })
				.set(ghost, { x: words.left, y: words.top, width: 0, height: 0, autoAlpha: 1 })
				.to(layout!, { x: words.left + words.width, y: words.top + words.height, duration: 0.9, ease: 'power1.inOut' })
				.to(
					ghost,
					{
						width: words.width,
						height: words.height,
						duration: 0.9,
						ease: 'power1.inOut',
						onUpdate: () => {
							const size = ghost.getBoundingClientRect();

							badge = `${Math.round(size.width)} × ${Math.round(size.height)}`;
						}
					},
					'<'
				)
				.to(ghost, { autoAlpha: 0, duration: 0.3 }, '>0.4')
				.to(layout!, { x: card.offsetWidth + 60, y: words.top, duration: 0.8, ease: 'power2.in' }, '<')
				.set(layout!, { autoAlpha: 0 }),
			0.2
		);

		return timeline;
	}

	async function copyEmail(): Promise<void> {
		try {
			await navigator.clipboard.writeText(EMAIL);
		} catch {
			// some browsers refuse the clipboard; the address is still on screen as a mail link
			return;
		}

		copied = true;
		setTimeout(() => (copied = false), COPIED_FOR_MS);

		if (!window.matchMedia(MOTION).matches) {
			return;
		}

		gsap.fromTo(
			gsap.utils.selector(root!)('.burst i'),
			{ x: 0, y: 0, scale: 1, autoAlpha: 1, rotation: 0 },
			{
				x: (index: number) => `${Math.cos((index / BURST.length) * Math.PI * 2) * 4}rem`,
				y: (index: number) => `${Math.sin((index / BURST.length) * Math.PI * 2) * 3}rem`,
				rotation: 'random(-120, 120)',
				scale: 0,
				autoAlpha: 0,
				duration: 0.7,
				ease: 'power2.out'
			}
		);
	}

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(MOTION, () => {
				const split = SplitText.create('.words', { type: 'chars', mask: 'chars' });

				// a mask is only as tall as the line, which is shorter than the letters: make room below for the y
				gsap.set(split.masks, { paddingBottom: '0.2em', marginBottom: '-0.2em' });

				gsap.fromTo(
					'.card',
					{ scale: 0.8, borderRadius: '5rem' },
					{
						scale: 1,
						borderRadius: '2rem',
						ease: 'none',
						scrollTrigger: { trigger: root, start: 'top bottom', end: 'top top', scrub: 0.6 }
					}
				);

				gsap.timeline({ scrollTrigger: { trigger: root, start: 'top 45%' } })
					.from(split.chars, { yPercent: 115, duration: 0.9, stagger: 0.05, ease: 'power4.out' })
					.from('.drop', { yPercent: -110, duration: 1.1, stagger: 0.15, ease: 'bounce.out' }, 0.2)
					.add(() => {
						assemble(root!.querySelector('.card')!);
					}, 0);

				gsap.set(['.mail', '.github'], { y: '100vh' });

				gsap.utils.toArray<HTMLElement>('.swing').forEach((charm, index) => {
					gsap.fromTo(
						charm,
						{ rotation: -7 },
						{ rotation: 7, duration: 1.6 + index * 0.3, ease: 'sine.inOut', yoyo: true, repeat: -1 }
					);
				});
			});

			media.add(POINTER_MOTION, () => {
				const charms = gsap.utils.toArray<HTMLElement>('.lean').map((charm) => ({
					charm,
					lean: gsap.quickTo(charm, 'rotation', { duration: 0.8, ease: 'power3.out' })
				}));

				const avoid = (event: PointerEvent): void => {
					for (const { charm, lean } of charms) {
						const box = charm.getBoundingClientRect();
						const away = box.left + box.width / 2 - event.clientX;
						const near = Math.max(0, 1 - Math.abs(away) / 320);

						lean(Math.sign(away) * near * -22);
					}
				};

				window.addEventListener('pointermove', avoid);

				return () => window.removeEventListener('pointermove', avoid);
			});
		}, root);

		return () => context.revert();
	});
</script>

<section class="hi" id="hi" bind:this={root}>
	<div class="card">
		<KeyRain />

		<h2 class="words">say hi</h2>

		{#each [{ side: 'left', string: 150 }, { side: 'right', string: 100 }] as charm (charm.side)}
			<div class="drop {charm.side}">
				<div class="lean">
					<div class="swing">
						<Charm string={charm.string} />
					</div>
				</div>
			</div>
		{/each}

		<div class="ghost" aria-hidden="true"><span>{badge}</span></div>

		{#each HANDS as hand (hand.name)}
			<div class="hand {hand.tone}" aria-hidden="true">
				<svg viewBox="0 0 18 23"><path d="M2 2 2 18 6.8 13.6 10.4 21.4 13 20.2 9.5 12.6 16 12.6Z" /></svg>
				<span>{hand.name}</span>
			</div>
		{/each}

		<div class="actions">
			<span class="wave"><Emoji code="1f44b" char="👋" /></span>
			<p class="mail">
				<a href="mailto:{EMAIL}">{EMAIL}</a>
				<button type="button" onclick={copyEmail} aria-live="polite">
					{copied ? 'copied' : 'copy'}
					<span class="burst" aria-hidden="true">
						{#each BURST as shard (shard)}
							<i></i>
						{/each}
					</span>
				</button>
			</p>
			<a class="github" href={GITHUB} target="_blank" rel="noreferrer">github ↗</a>
		</div>

		<footer>
			<div class="lace" aria-hidden="true">
				{#each SCALLOPS as scallop (scallop)}
					<i style:--order={scallop}></i>
				{/each}
			</div>
			<p>© 2026 belikhun · served by harbor · <a class="key" href={GPG_KEY_FILE} download>pgp {GPG_KEY_ID}</a></p>
		</footer>
	</div>
</section>

<style lang="scss">
	.hi {
		height: 100svh;
		min-height: 36rem;
		padding: 0.75rem;
	}

	.card {
		position: relative;
		display: grid;
		grid-template-rows: 1fr auto auto;
		justify-items: center;
		height: 100%;
		border-radius: 2rem;
		background: var(--sky);
		overflow: hidden;
		// the key rain sits behind everything else in the card, but in front of its sky
		isolation: isolate;
	}

	.words {
		@include display;
		align-self: center;
		font-size: clamp(6rem, 24vw, 28rem);
		color: var(--wordmark);
		white-space: nowrap;
	}

	.drop {
		position: absolute;
		top: 0;
		width: clamp(3.5rem, 6vw, 5.5rem);

		&.left {
			left: 22%;
		}

		&.right {
			right: 24%;
		}
	}

	.lean,
	.swing {
		transform-origin: 50% 0%;
	}

	.actions {
		position: relative;
		z-index: 1;
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.75rem;
		padding: 0 1rem 4.5rem;
	}

	.mail,
	.github {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1.5rem;
		border-radius: 2rem;
		background: var(--bg);
		font-weight: 500;
	}

	.wave {
		@include below($bp-narrow) {
			display: none !important;
		}

		display: grid;
		place-items: center;
		padding: 0.5rem 0.875rem;
		border-radius: 2rem;
		background: var(--bg);
		font-size: 1.5rem;
		line-height: 1;
	}

	.mail button {
		@include bare-button;
		position: relative;
		color: var(--accent-text);
		font-weight: 600;
	}

	.burst {
		position: absolute;
		top: 50%;
		left: 50%;

		i {
			position: absolute;
			width: 0.5rem;
			aspect-ratio: 3 / 5;
			clip-path: polygon(30% 0, 100% 18%, 70% 100%, 0 82%);
			background: var(--purple);
			visibility: hidden;

			&:nth-child(even) {
				background: var(--pink);
			}
		}
	}

	.ghost {
		position: absolute;
		top: 0;
		left: 0;
		border: 0.125rem dashed var(--purple);
		border-radius: 0.25rem;
		background: color-mix(in srgb, var(--purple) 12%, transparent);
		visibility: hidden;
		pointer-events: none;

		span {
			@include label;
			position: absolute;
			top: 100%;
			right: 0;
			margin-top: 0.375rem;
			padding: 0.125rem 0.5rem;
			border-radius: 0.25rem;
			background: var(--purple);
			color: var(--paper);
			white-space: nowrap;
		}
	}

	.hand {
		position: absolute;
		top: 0;
		left: 0;
		z-index: 2;
		display: flex;
		align-items: flex-start;
		visibility: hidden;
		pointer-events: none;

		svg {
			width: 1.25rem;
			fill: var(--pink);
			stroke: var(--night);
			stroke-width: 1.2;
			stroke-linejoin: round;
		}

		span {
			margin: 1rem 0 0 0.125rem;
			padding: 0.125rem 0.625rem;
			border-radius: 0.75rem;
			background: var(--pink);
			color: var(--night);
			font-size: 0.75rem;
			font-weight: 500;
			white-space: nowrap;
		}

		&.blue {
			svg {
				fill: var(--blue);
			}

			span {
				background: var(--blue);
			}
		}

		&.paper {
			svg {
				fill: var(--paper);
			}

			span {
				background: var(--paper);
			}
		}
	}

	footer {
		@include label;
		position: relative;
		z-index: 1;
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.25rem 2rem;
		width: 100%;
		padding: 1.5rem 1rem 1rem;
		background: var(--bg);
		text-align: center;
		color: var(--soft);
	}

	.key {
		white-space: nowrap;
	}

	// the lace border from the illustration: a row of scallops along the top of the footer, rolling like a wave
	.lace {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 100%;
		display: flex;
		justify-content: center;
		height: 3rem;
		overflow: hidden;

		i {
			flex: none;
			width: 5rem;
			height: 5rem;
			margin-inline: -0.75rem;
			border-radius: 50%;
			background: var(--bg);
			translate: 0 20%;

			@include motion {
				animation: swell 3.6s ease-in-out infinite;
				animation-delay: calc(var(--order) * -0.3s);
			}
		}
	}

	@keyframes swell {
		0%,
		100% {
			translate: 0 34%;
		}

		50% {
			translate: 0 4%;
		}
	}
</style>
