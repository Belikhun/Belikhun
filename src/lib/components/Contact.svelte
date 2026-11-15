<!-- Copyright (c) 2026 Belikhun. Licensed under the MIT License.
     See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { EMAIL, EMAIL_SECONDARY, GITHUB, GPG_KEY_FILE, GPG_KEY_ID, SOCIALS } from '#lib/content/site.ts';
	import { gsap, MOTION, POINTER_MOTION, ScrollTrigger, SplitText } from '#lib/motion/gsap.ts';

	import Charm, { type Face } from './Charm.svelte';
	import Emoji from './Emoji.svelte';
	import KeyRain from './KeyRain.svelte';

	const COPIED_FOR_MS = 1800;
	const BURST = [0, 1, 2, 3, 4, 5];

	/** The cursors that build the ending, named after the job each one does. */
	const HANDS = [
		{ name: 'layout', tone: 'pink' },
		{ name: 'type', tone: 'blue' },
		{ name: 'mail', tone: 'paper' },
		{ name: 'links', tone: 'lav' },
		{ name: 'lace', tone: 'purple' }
	];

	/** What a cursor looks like while it works: pointing, dragging out a box, or typing. */
	type Shape = 'arrow' | 'cross' | 'beam';

	/** Seconds between two letters, for the big words, for a button and for the small print. */
	const PACE = { words: 0.12, button: 0.035, print: 0.012 };

	/** The two charms that drop into the card, each with its own string, face and side. */
	const CHARMS: { side: string; string: number; face: Face; flip: boolean }[] = [
		{ side: 'left', string: 150, face: 'happy', flip: false },
		{ side: 'right', string: 100, face: 'calm', flip: true }
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

	/** Where a part sits inside the card, in the card's own unscaled pixels. */
	function boxOf(card: HTMLElement, part: Element): Box {
		const frame = card.getBoundingClientRect();
		const place = part.getBoundingClientRect();
		const scale = frame.width / card.offsetWidth;

		return {
			left: (place.left - frame.left) / scale,
			top: (place.top - frame.top) / scale,
			width: place.width / scale,
			height: place.height / scale
		};
	}

	/** One cursor: the outline it drags, the label on that outline, and its own queue of steps. */
	interface Worker {
		hand: HTMLElement;
		ghost: HTMLElement;
		badge: HTMLElement;
		line: gsap.core.Timeline;
	}

	/**
	 * Five cursors build the ending the way it would be laid out in a design
	 * tool, then leave: boxes are dragged out and measured, words are typed
	 * letter by letter, a button is copied into the next, the charms are pulled
	 * down on their strings and the lace is laid along the footer. Every part
	 * was hidden by the caller; nothing shows until a cursor has made it.
	 */
	function assemble(card: HTMLElement): gsap.core.Timeline {
		const find = (selector: string): HTMLElement[] => gsap.utils.toArray<HTMLElement>(selector, card);
		const one = (selector: string): HTMLElement => card.querySelector<HTMLElement>(selector)!;
		const lettersOf = (part: Element): HTMLElement[] => gsap.utils.toArray<HTMLElement>('.glyph', part);
		const ghosts = find('.ghost');

		const workers = find('.hand').map((hand, index): Worker => ({
			hand,
			ghost: ghosts[index]!,
			badge: ghosts[index]!.querySelector('span')!,
			line: gsap.timeline()
		}));

		const [layout, typist, mail, links, lace] = workers as [Worker, Worker, Worker, Worker, Worker];
		const width = card.offsetWidth;
		const height = card.offsetHeight;

		const shape = (worker: Worker, look: Shape): void => {
			worker.line.set(worker.hand, { attr: { 'data-shape': look } });
		};

		/** Holds a worker until `seconds` into the build, when it is not there yet. */
		const wait = (worker: Worker, seconds: number): void => {
			const spare = seconds - worker.line.duration();

			if (spare > 0) {
				worker.line.to({}, { duration: spare });
			}
		};

		const enter = (worker: Worker, x: number, y: number): void => {
			shape(worker, 'arrow');
			worker.line.set(worker.hand, { x, y, autoAlpha: 1 });
		};

		const leave = (worker: Worker, x: number, y: number): void => {
			shape(worker, 'arrow');
			worker.line
				.to(worker.hand, { x, y, duration: 0.7, ease: 'power2.in' }, '>0.1')
				.set(worker.hand, { autoAlpha: 0 });
		};

		/** Drags a box out over a part, corner to corner, with its size on a label; the part then appears in it. */
		const draw = (worker: Worker, part: Element, seconds: number, appears = true): void => {
			const box = boxOf(card, part);

			shape(worker, 'cross');
			worker.line
				.to(worker.hand, { x: box.left, y: box.top, duration: 0.4, ease: 'power2.inOut' })
				.set(worker.ghost, {
					x: box.left,
					y: box.top,
					width: 0,
					height: 0,
					autoAlpha: 1,
					borderRadius: getComputedStyle(part).borderRadius
				})
				.to(worker.hand, { x: box.left + box.width, y: box.top + box.height, duration: seconds, ease: 'power1.inOut' })
				.to(
					worker.ghost,
					{
						width: box.width,
						height: box.height,
						duration: seconds,
						ease: 'power1.inOut',
						onUpdate: () => {
							worker.badge.textContent = `${Math.round(Number(gsap.getProperty(worker.ghost, 'width')))} × ${Math.round(Number(gsap.getProperty(worker.ghost, 'height')))}`;
						}
					},
					'<'
				);

			if (appears) {
				worker.line.to(part, { autoAlpha: 1, duration: 0.3 });
			}

			worker.line.to(worker.ghost, { autoAlpha: 0, duration: 0.3 }, appears ? '<' : '>0.15');
		};

		/** Types a part's letters one at a time, the cursor a text beam just past the last one. */
		const type = (worker: Worker, part: Element, pace: number): void => {
			const letters = lettersOf(part);

			if (letters.length === 0) {
				return;
			}

			const first = boxOf(card, letters[0]!);

			shape(worker, 'beam');
			worker.line.to(worker.hand, { x: first.left, y: first.top + first.height / 2, duration: 0.35, ease: 'power2.inOut' });

			for (const letter of letters) {
				const box = boxOf(card, letter);

				worker.line
					.set(worker.hand, { x: box.left + box.width, y: box.top + box.height / 2 }, `>${pace}`)
					.set(letter, { autoAlpha: 1 }, '<');
			}
		};

		/** Picks one finished part up and drags a copy of its outline to where the next part goes. */
		const copy = (worker: Worker, source: Element, part: Element): void => {
			const from = boxOf(card, source);
			const to = boxOf(card, part);

			shape(worker, 'arrow');
			worker.line
				.to(worker.hand, { x: from.left + from.width / 2, y: from.top + from.height / 2, duration: 0.35, ease: 'power2.inOut' })
				.set(worker.ghost, {
					x: from.left,
					y: from.top,
					width: from.width,
					height: from.height,
					autoAlpha: 1,
					borderRadius: getComputedStyle(source).borderRadius
				})
				.call(() => {
					worker.badge.textContent = 'copy';
				})
				.to(worker.hand, { x: to.left + to.width / 2, y: to.top + to.height / 2, duration: 0.45, ease: 'power2.inOut' })
				.to(worker.ghost, { x: to.left, y: to.top, width: to.width, height: to.height, duration: 0.45, ease: 'power2.inOut' }, '<')
				.to(part, { autoAlpha: 1, duration: 0.25 })
				.to(worker.ghost, { autoAlpha: 0, duration: 0.25 }, '<');
		};

		const words = one('.words');
		const footer = one('footer');
		const guide = one('.guide');
		const actions = boxOf(card, one('.actions'));

		// layout: a guide for the buttons to sit on, the box the words are typed into, then the footer
		enter(layout, width * 0.3, -30);
		layout.line
			.set(guide, { y: 0, autoAlpha: 1 })
			.to(layout.hand, { y: actions.top, duration: 0.6, ease: 'power2.out' })
			.to(guide, { y: actions.top, duration: 0.6, ease: 'power2.out' }, '<');
		draw(layout, words, 0.8, false);

		const wordsBoxed = layout.line.duration();

		draw(layout, footer, 0.7);

		const footerBuilt = layout.line.duration();

		leave(layout, width + 60, height * 0.5);

		// type: the words, then the small print once there is a footer to hold it
		wait(typist, wordsBoxed - 0.6);
		enter(typist, -40, height * 0.4);
		type(typist, words, PACE.words);
		wait(typist, footerBuilt);

		for (const line of find('footer p')) {
			type(typist, line, PACE.print);
		}

		leave(typist, -60, height * 0.9);

		// mail: the wave, then the address in its button
		wait(mail, 0.7);
		enter(mail, width * 0.45, height + 30);

		// the wave is not shown on a narrow screen
		if (one('.wave').offsetParent) {
			draw(mail, one('.wave'), 0.3);
		}

		draw(mail, one('.mail'), 0.6);
		type(mail, one('.mail a'), PACE.button);
		mail.line.to(one('.mail button'), { autoAlpha: 1, duration: 0.3 });
		leave(mail, -60, height * 0.7);

		// links: one button drawn and typed, the rest copied from it and retyped
		wait(links, 1);
		enter(links, width * 0.6, height + 30);
		draw(links, one('.github'), 0.5);
		type(links, one('.github'), PACE.button);

		for (const social of find('.social')) {
			copy(links, one('.github'), social);
			type(links, social, PACE.button);
		}

		leave(links, width + 60, height * 0.8);

		// lace: pulls each charm down on its string, then lays the lace along the footer
		wait(lace, 0.4);

		for (const drop of find('.drop')) {
			const x = drop.offsetLeft + drop.offsetWidth / 2;

			shape(lace, 'arrow');
			lace.line
				.set(lace.hand, { x, y: -30, autoAlpha: 1 })
				.to(lace.hand, { y: drop.offsetHeight * 0.8, duration: 0.8, ease: 'back.out(1.6)' })
				.to(drop, { yPercent: 0, duration: 0.8, ease: 'back.out(1.6)' }, '<')
				.to(lace.hand, { y: -30, duration: 0.4, ease: 'power2.in' }, '>0.1');
		}

		wait(lace, footerBuilt);

		const edge = boxOf(card, one('.lace'));
		const sweep = 1.2;

		lace.line
			.set(lace.hand, { x: -30, y: edge.top + edge.height / 2 })
			.to(lace.hand, { x: width + 30, duration: sweep, ease: 'none' })
			.to(
				find('.lace i'),
				{
					'--grow': 1,
					duration: 0.45,
					ease: 'back.out(2)',
					// each scallop pops up as the cursor passes over it
					stagger: (_index: number, scallop: Element) => {
						const box = boxOf(card, scallop);

						return gsap.utils.clamp(0, 1, (box.left + box.width / 2) / width) * sweep;
					}
				},
				'<'
			)
			.set(lace.hand, { autoAlpha: 0 });

		const build = gsap.timeline();

		for (const worker of workers) {
			build.add(worker.line, 0);
		}

		return build.to(guide, { autoAlpha: 0, duration: 0.4 }, '>-0.4');
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
				// Everything a cursor will type is split into letters. The small print keeps its own
				// accessibility tree: its links would be hidden from a screen reader otherwise.
				// (a button is a flex row, so its letters are split inside one child, where its gap cannot fall between them)
				SplitText.create(['.words', '.mail a', '.typed'], { type: 'chars', charsClass: 'glyph' });
				SplitText.create('footer p', { type: 'chars', charsClass: 'glyph', aria: 'none' });

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

				// nothing in the card is there until a cursor has drawn, typed, copied or pulled it into place
				gsap.set(['.glyph', '.wave', '.mail', '.mail button', '.github', '.social', 'footer'], { autoAlpha: 0 });
				// through a variable, not a transform: GSAP would fold the scallops' own `translate` into its
				// transform and the wave's keyframes would then push them that much further down
				gsap.set('.lace i', { '--grow': 0 });
				gsap.set('.drop', { yPercent: -110 });

				ScrollTrigger.create({
					trigger: root,
					start: 'top 45%',
					once: true,
					onEnter: () => {
						assemble(root!.querySelector('.card')!);
					}
				});

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

		{#each CHARMS as charm (charm.side)}
			<div class="drop {charm.side}">
				<div class="lean">
					<div class="swing">
						<Charm string={charm.string} face={charm.face} flip={charm.flip} />
					</div>
				</div>
			</div>
		{/each}

		<div class="guide" aria-hidden="true"></div>

		{#each HANDS as hand (hand.name)}
			<div class="ghost" aria-hidden="true"><span></span></div>
		{/each}

		{#each HANDS as hand (hand.name)}
			<div class="hand {hand.tone}" data-shape="arrow" aria-hidden="true">
				<svg class="arrow" viewBox="0 0 18 23"><path d="M2 2 2 18 6.8 13.6 10.4 21.4 13 20.2 9.5 12.6 16 12.6Z" /></svg>
				<svg class="cross" viewBox="0 0 18 18"><path d="M9 1V17M1 9H17" /></svg>
				<svg class="beam" viewBox="0 0 10 22"><path d="M1 1H9M5 1V21M1 21H9" /></svg>
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
			<a class="github" href={GITHUB} target="_blank" rel="noreferrer"><span class="typed">github ↗</span></a>
			{#each SOCIALS as social (social.name)}
				<a class="social" href={social.href} target="_blank" rel="noreferrer"><span class="typed">{social.name} ↗</span></a>
			{/each}
		</div>

		<footer>
			<div class="lace" aria-hidden="true">
				{#each SCALLOPS as scallop (scallop)}
					<i style:--order={scallop}></i>
				{/each}
			</div>
			<p>© 2026 belikhun · served by harbor · <a class="key" href={GPG_KEY_FILE} download>pgp {GPG_KEY_ID}</a></p>
			<p>also at <a class="key" href="mailto:{EMAIL_SECONDARY}">{EMAIL_SECONDARY}</a></p>
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
	.github,
	.social {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		@include glass;
		padding: 0.75rem 1.5rem;
		border-radius: 2rem;
		font-weight: 500;
	}

	.wave {
		@include below($bp-narrow) {
			display: none !important;
		}

		display: grid;
		place-items: center;
		@include glass;
		padding: 0.5rem 0.875rem;
		border-radius: 2rem;
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
		z-index: 2;
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

	// the line the buttons are set on while the ending is built
	.guide {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		z-index: 2;
		height: 0.1rem;
		background: var(--pink);
		visibility: hidden;
		pointer-events: none;
	}

	.hand {
		--tone: var(--pink);
		position: absolute;
		top: 0;
		left: 0;
		z-index: 3;
		visibility: hidden;
		pointer-events: none;

		// one of the three is shown at a time; the box and text cursors sit centred on the point they work at
		svg {
			display: none;
			stroke: var(--night);
			stroke-linejoin: round;
			stroke-linecap: round;
		}

		.arrow {
			width: 1.25rem;
			fill: var(--tone);
			stroke-width: 1.2;
		}

		.cross,
		.beam {
			position: absolute;
			top: 0;
			left: 0;
			fill: none;
			stroke-width: 2;
			translate: -50% -50%;
		}

		.cross {
			width: 1.25rem;
		}

		.beam {
			width: 0.625rem;
		}

		// the shape is set by script, which the compiler cannot see
		&:global([data-shape='arrow']) .arrow,
		&:global([data-shape='cross']) .cross,
		&:global([data-shape='beam']) .beam {
			display: block;
		}

		span {
			position: absolute;
			top: 1rem;
			left: 0.75rem;
			padding: 0.125rem 0.625rem;
			border-radius: 0.75rem;
			background: var(--tone);
			color: var(--night);
			font-size: 0.75rem;
			font-weight: 500;
			white-space: nowrap;
		}

		&.blue {
			--tone: var(--blue);
		}

		&.paper {
			--tone: var(--paper);
		}

		&.lav {
			--tone: var(--lav);
		}

		&.purple {
			--tone: var(--purple);

			span {
				color: var(--paper);
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
			// 0 until a cursor lays the lace, where the ending is built by cursors
			scale: var(--grow, 1);

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
