<!-- Copyright (c) 2026 Belikhun. Licensed under the MIT License.
     See LICENSE at the repository root. -->

<script lang="ts">
	import { gsap, type Span } from '#lib/motion/gsap.ts';

	const PLAYERS = 20000;

	/** The four answers and the share of the room that picked each, in percent. */
	const ANSWERS = [
		{ mark: '▲', text: 'a message queue', share: 14, tone: 'red' },
		{ mark: '◆', text: 'an mqtt broker', share: 61, tone: 'blue', right: true },
		{ mark: '●', text: 'a cron job', share: 9, tone: 'yellow' },
		{ mark: '■', text: 'a load balancer', share: 16, tone: 'green' }
	];

	const BOARD = [
		{ name: 'mai', score: 9840 },
		{ name: 'khoa', score: 9615 },
		{ name: 'linh', score: 9402 }
	];

	const FORMAT = new Intl.NumberFormat('en-US');

	let root = $state<HTMLDivElement>();
	let joined = $state(PLAYERS);
	let seconds = $state(0);

	/**
	 * Plays one round: the room fills, the clock runs out, the answers come in and the board settles.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 * @param shown the stretch of the timeline over which this card is on screen
	 */
	export function animate(timeline: gsap.core.Timeline, at: number, shown: Span): void {
		const scope = gsap.utils.selector(root!);
		const room = { players: 0, clock: 20 };

		timeline
			.fromTo(scope('.flower'), { rotation: -90 }, { rotation: 90, duration: shown.to - shown.from, ease: 'none' }, shown.from)
			.fromTo(
				room,
				{ players: 0 },
				{
					players: PLAYERS,
					duration: 0.22,
					ease: 'power2.in',
					onUpdate: () => {
						joined = Math.round(room.players / 10) * 10;
					}
				},
				at
			)
			.from(scope('.question'), { y: '1.5rem', autoAlpha: 0, duration: 0.06, ease: 'power2.out' }, at + 0.04)
			.from(scope('.answer'), { scale: 0.8, autoAlpha: 0, duration: 0.05, stagger: 0.02, ease: 'back.out(2)' }, at + 0.08)
			.fromTo(
				room,
				{ clock: 20 },
				{
					clock: 0,
					duration: 0.18,
					ease: 'none',
					onUpdate: () => {
						seconds = Math.ceil(room.clock);
					}
				},
				at + 0.14
			)
			.fromTo(scope('.ring'), { '--left': 1 }, { '--left': 0, duration: 0.18, ease: 'none' }, at + 0.14)
			.from(scope('.fill'), { scaleX: 0, duration: 0.08, stagger: 0.01, ease: 'power2.out' }, at + 0.32)
			.to(scope('.answer:not(.right)'), { opacity: 0.45, duration: 0.04 }, at + 0.38)
			.from(scope('.row'), { x: '2rem', autoAlpha: 0, duration: 0.05, stagger: 0.02, ease: 'power2.out' }, at + 0.4);
	}
</script>

<div class="arena" bind:this={root}>
	<img class="flower" src="/img/vloom/vloom-symbol-white.svg" width="195" height="184" alt="" />

	<header>
		<p class="brand">
			<img src="/img/vloom/vloom-symbol.svg" width="195" height="184" alt="" />
			Vloom Arena
		</p>
		<p class="room"><strong>{FORMAT.format(joined)}</strong> players</p>
	</header>

	<div class="question">
		<p class="step">question 4 of 10</p>
		<p class="ask">what fans one answer out to twenty thousand screens?</p>
		<span class="ring" aria-hidden="true">{seconds}</span>
	</div>

	<ul class="answers">
		{#each ANSWERS as answer (answer.text)}
			<li class="answer {answer.tone}" class:right={answer.right}>
				<span class="mark" aria-hidden="true">{answer.mark}</span>
				<span class="text">{answer.text}</span>
				<span class="share">{answer.share}%</span>
				<i class="fill" style:width="{answer.share}%"></i>
			</li>
		{/each}
	</ul>

	<ol class="board">
		{#each BOARD as player, index (player.name)}
			<li class="row">
				<span>{index + 1}</span>
				<strong>{player.name}</strong>
				<span>{FORMAT.format(player.score)}</span>
			</li>
		{/each}
	</ol>
</div>

<style lang="scss">
	// Vloom's brand colours, from its media kit
	$pink: #f65d6f;
	$pink-light: #ffbbc7;
	$charcoal: #333333;

	.arena {
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		align-content: center;
		gap: 1rem;
		height: 100%;
		min-height: 20rem;
		padding: 1.5rem;
		border-radius: 1.5rem;
		background: radial-gradient(circle at 80% 0%, #4a2a36, #241a22 60%);
		color: #ffffff;
		overflow: hidden;
		isolation: isolate;
	}

	.flower {
		position: absolute;
		z-index: -1;
		right: -16%;
		bottom: -30%;
		width: 70%;
		height: auto;
		opacity: 0.07;
	}

	header {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem 1rem;
	}

	.brand {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-family: var(--display);
		font-size: 1.25rem;
		font-weight: 800;

		img {
			width: 1.75rem;
			height: auto;
		}
	}

	.room {
		padding: 0.25rem 1rem;
		border-radius: 2rem;
		background: rgba(255, 255, 255, 0.12);
		font-size: 0.875rem;

		strong {
			font-weight: 600;
			font-variant-numeric: tabular-nums;
		}
	}

	.question {
		position: relative;
		display: grid;
		gap: 0.5rem;
		padding: 1.25rem 5.5rem 1.25rem 1.5rem;
		border-radius: 1rem;

		@include below($bp-narrow) {
			padding: 1rem 3.75rem 1rem 1rem;
		}
		background: #ffffff;
		color: $charcoal;
	}

	.step {
		@include label;
		color: $pink;
	}

	.ask {
		font-family: var(--display);
		font-size: clamp(1.25rem, 2vw, 1.75rem);
		font-weight: 800;
		line-height: 1.1;
	}

	.ring {
		--left: 0;
		position: absolute;
		top: 50%;
		right: 1.25rem;
		display: grid;
		place-items: center;
		width: 3.5rem;
		height: 3.5rem;

		@include below($bp-narrow) {
			right: 0.75rem;
			width: 2.5rem;
			height: 2.5rem;
			font-size: 0.875rem;
		}
		margin-top: -1.75rem;
		border-radius: 50%;
		background:
			radial-gradient(circle, #ffffff 58%, transparent 60%),
			conic-gradient($pink calc(var(--left) * 360deg), $pink-light 0);
		font-family: var(--mono);
		font-weight: 500;
		font-variant-numeric: tabular-nums;
	}

	.answers {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 0.625rem;

		@include below($bp-narrow) {
			grid-template-columns: minmax(0, 1fr);
		}
	}

	.answer {
		position: relative;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.875rem 1rem;
		border-radius: 0.75rem;
		background: #d94a5c;
		font-weight: 500;
		overflow: hidden;

		&.blue {
			background: #3f7fd9;
		}

		&.yellow {
			background: #d99a1f;
		}

		&.green {
			background: #2f9e44;
		}

		&.right {
			box-shadow: 0 0 0 0.1875rem #ffffff;
		}

		> span {
			position: relative;
			z-index: 1;
		}
	}

	.text {
		flex: 1;
		min-width: 0;
	}

	.share {
		font-family: var(--mono);
		font-size: 0.875rem;
	}

	.fill {
		position: absolute;
		inset: 0 auto 0 0;
		background: rgba(0, 0, 0, 0.22);
		transform-origin: 0 50%;
	}

	.board {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 0.625rem;

		@include below($bp-narrow) {
			grid-template-columns: minmax(0, 1fr);
		}
	}

	.row {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		padding: 0.5rem 0.875rem;
		border-radius: 0.75rem;
		background: rgba(255, 255, 255, 0.1);
		font-family: var(--mono);
		font-size: 0.75rem;

		strong {
			flex: 1;
			font-family: var(--body);
			font-size: 0.875rem;
			font-weight: 500;
		}

		&:first-child {
			background: $pink;
		}
	}
</style>
