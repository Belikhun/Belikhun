<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onDestroy } from 'svelte';

	import { gsap } from '#lib/motion/gsap.ts';

	// The idea of cursors building the page comes from Joel Califa's Swarm
	// (califa.github.io/swarm-site). Nothing here is taken from it: the cursors,
	// the choreography and the code are this site's own.

	const TITLE = 'counter';

	/** Each cursor is named after a part of Clover; x and y are where it rests. */
	const CURSORS = [
		{ name: 'compiler', tone: 'pink', x: '8%', y: '78%' },
		{ name: 'runtime', tone: 'blue', x: '70%', y: '14%' },
		{ name: 'language server', tone: 'lav', x: '62%', y: '84%' }
	];

	interface Box {
		left: number;
		top: number;
		width: number;
		height: number;
	}

	let root = $state<HTMLDivElement>();
	let typed = $state(TITLE);
	let count = $state(3);
	let badge = $state('');

	let played = false;
	let context: gsap.Context | undefined;

	function boxOf(selector: string): Box {
		const stage = root!.getBoundingClientRect();
		const part = root!.querySelector(selector)!.getBoundingClientRect();

		return { left: part.left - stage.left, top: part.top - stage.top, width: part.width, height: part.height };
	}

	/** Where a resting cursor has to travel to put its tip on a point of the stage. */
	function reach(cursor: HTMLElement, left: number, top: number): gsap.TweenVars {
		return { x: left - cursor.offsetLeft, y: top - cursor.offsetTop };
	}

	/** Adds one cursor dragging a box out from its top-left corner, then the real part fading in. */
	function drag(timeline: gsap.core.Timeline, cursor: HTMLElement, ghost: Element, part: string): void {
		const box = boxOf(part);

		timeline
			.to(cursor, { ...reach(cursor, box.left, box.top), duration: 0.55, ease: 'power2.inOut' })
			.set(ghost, { x: box.left, y: box.top, width: 0, height: 0, autoAlpha: 1 })
			.to(cursor, { ...reach(cursor, box.left + box.width, box.top + box.height), duration: 0.6, ease: 'power1.inOut' })
			.to(
				ghost,
				{
					width: box.width,
					height: box.height,
					duration: 0.6,
					ease: 'power1.inOut',
					onUpdate: () => {
						const size = ghost.getBoundingClientRect();

						badge = `${Math.round(size.width)} × ${Math.round(size.height)}`;
					}
				},
				'<'
			)
			.to(root!.querySelector(part), { autoAlpha: 1, duration: 0.25 })
			.set(ghost, { autoAlpha: 0 });
	}

	function play(): void {
		if (played) {
			return;
		}

		played = true;

		context = gsap.context(() => {
			const [compiler, runtime, server] = gsap.utils.toArray<HTMLElement>('.cursor');
			const ghost = root!.querySelector('.ghost')!;
			const title = boxOf('.title');
			const button = boxOf('.button');
			const letters = { shown: 0 };
			const build = gsap.timeline();

			drag(build, compiler!, ghost, '.panel');

			build
				.to(runtime!, { ...reach(runtime!, title.left, title.top + title.height * 0.6), duration: 0.5, ease: 'power2.inOut' }, '-=0.4')
				.set('.title', { autoAlpha: 1 })
				.to(letters, {
					shown: TITLE.length,
					duration: 0.7,
					ease: `steps(${TITLE.length})`,
					onUpdate: () => {
						typed = TITLE.slice(0, Math.round(letters.shown));
					}
				});

			drag(build, server!, ghost, '.button');

			build
				.fromTo('.number', { autoAlpha: 0, scale: 0.4 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: 'back.out(2.5)' })
				.to(compiler!, { x: '-=40', y: '+=60', duration: 0.6, ease: 'power2.inOut' }, '<')
				.to(runtime!, { x: '+=120', y: '-=50', duration: 0.6, ease: 'power2.inOut' }, '<')
				.to(server!, { ...reach(server!, button.left + button.width * 0.6, button.top + button.height * 0.6), duration: 0.4, ease: 'power2.inOut' })
				.add(
					gsap.timeline({ repeat: -1, repeatDelay: 1.1 })
						.to(server!, { scale: 0.8, duration: 0.08, yoyo: true, repeat: 1 })
						.call(() => {
							count += 1;
						})
						.fromTo('.number', { scale: 1.25 }, { scale: 1, duration: 0.3, ease: 'power2.out' })
				);
		}, root);
	}

	/**
	 * Blanks the component, then lets the cursors rebuild it once this card arrives.
	 * The build runs on its own clock; scrolling only starts it.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 */
	export function animate(timeline: gsap.core.Timeline, at: number): void {
		typed = '';
		count = 0;
		gsap.set(gsap.utils.selector(root!)('.part'), { autoAlpha: 0 });
		timeline.call(play, [], at + 0.02);
	}

	onDestroy(() => context?.revert());
</script>

<div class="clover" bind:this={root}>
	<p class="file">counter.clover</p>

	<div class="panel part">
		<span class="title part">{typed}<i class="caret" aria-hidden="true"></i></span>
		<strong class="number part">{count}</strong>
		<button class="button part" type="button" onclick={() => (count += 1)}>+ 1</button>
	</div>

	<div class="ghost" aria-hidden="true"><span>{badge}</span></div>

	{#each CURSORS as cursor (cursor.name)}
		<div class="cursor {cursor.tone}" style:--x={cursor.x} style:--y={cursor.y} aria-hidden="true">
			<svg viewBox="0 0 18 23"><path d="M2 2 2 18 6.8 13.6 10.4 21.4 13 20.2 9.5 12.6 16 12.6Z" /></svg>
			<span>{cursor.name}</span>
		</div>
	{/each}
</div>

<style lang="scss">
	.clover {
		position: relative;
		display: grid;
		place-content: center;
		height: 100%;
		min-height: 20rem;
		border-radius: 1.5rem;
		background:
			radial-gradient(circle, var(--line) 0.0625rem, transparent 0.0625rem) 0 0 / 1.5rem 1.5rem,
			var(--bg);
		overflow: hidden;
	}

	.file {
		@include label;
		position: absolute;
		top: 1.5rem;
		left: 1.5rem;
		color: var(--soft);
	}

	.panel {
		display: grid;
		justify-items: center;
		gap: 0.75rem;
		width: 16rem;
		padding: 2rem;
		border: var(--hairline) solid var(--line);
		border-radius: 1.5rem;
		background: var(--surface);
		box-shadow: 0 1rem 2.5rem rgba(42, 36, 64, 0.12);
	}

	.title {
		@include label;
		min-height: 1.25rem;
		color: var(--soft);
	}

	.caret {
		display: inline-block;
		width: 0.0625rem;
		height: 1em;
		margin-left: 0.125rem;
		background: var(--purple);
		vertical-align: text-bottom;

		@include motion {
			animation: blink 0.9s steps(2) infinite;
		}
	}

	@keyframes blink {
		to {
			opacity: 0;
		}
	}

	.number {
		@include display;
		font-size: 5rem;
		font-variant-numeric: tabular-nums;
	}

	.button {
		@include bare-button;
		padding: 0.625rem 1.75rem;
		border-radius: 2rem;
		background: var(--purple);
		color: var(--paper);
		font-weight: 600;
	}

	.ghost {
		position: absolute;
		top: 0;
		left: 0;
		border: 0.0625rem solid var(--purple);
		background: color-mix(in srgb, var(--purple) 10%, transparent);
		visibility: hidden;

		span {
			@include label;
			position: absolute;
			top: 100%;
			left: 50%;
			margin-top: 0.375rem;
			padding: 0.125rem 0.5rem;
			border-radius: 0.25rem;
			background: var(--purple);
			color: var(--paper);
			white-space: nowrap;
			translate: -50% 0;
		}
	}

	.cursor {
		position: absolute;
		top: var(--y);
		left: var(--x);
		display: flex;
		align-items: flex-start;
		pointer-events: none;

		svg {
			width: 1.125rem;
			fill: var(--pink);
			stroke: var(--night);
			stroke-width: 1.2;
			stroke-linejoin: round;
		}

		span {
			margin: 0.875rem 0 0 0.125rem;
			padding: 0.125rem 0.5rem;
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

		&.lav {
			svg {
				fill: var(--lav);
			}

			span {
				background: var(--lav);
			}
		}
	}
</style>
