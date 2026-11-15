<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { EMAIL, GITHUB } from '#lib/content/site.ts';
	import { gsap, MOTION, POINTER_MOTION, SplitText } from '#lib/motion/gsap.ts';

	import Charm from './Charm.svelte';
	import Flock from './Flock.svelte';

	const COPIED_FOR_MS = 1800;
	const BURST = [0, 1, 2, 3, 4, 5];

	let root = $state<HTMLElement>();
	let copied = $state(false);

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
					.from('.actions > *', { y: '1.5rem', autoAlpha: 0, duration: 0.5, stagger: 0.1 }, 0.6);

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

		<Flock />

		<div class="actions">
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
			<p>© 2026 belikhun · served by Harbor</p>
			<p>
				the cursor swarm is a nod to
				<a href="https://califa.github.io/swarm-site/" target="_blank" rel="noreferrer">Swarm by Joel Califa</a>
			</p>
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
		padding: 0 1rem 2.5rem;
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

	.mail button {
		@include bare-button;
		position: relative;
		color: var(--purple);
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

	footer {
		@include label;
		position: relative;
		z-index: 1;
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.25rem 2rem;
		width: 100%;
		padding: 2.5rem 1rem 1rem;
		color: var(--soft);
		// the lace border from the illustration: a row of scallops cut into the sky
		background:
			radial-gradient(circle at 50% 0, transparent 0.875rem, var(--bg) 0.9375rem) 0 0 / 2rem 1.25rem repeat-x,
			linear-gradient(var(--bg), var(--bg)) 0 1.25rem / 100% 100% no-repeat;

		a {
			text-decoration: underline;
		}
	}
</style>
