<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { gsap, type Span } from '#lib/motion/gsap.ts';

	// Four panels of the contest page, not the whole page: the clock, the
	// submit box, a corner of the ranking and the log. One submission is
	// followed through them. The labels are the interface's own, so they stay
	// in Vietnamese and in their own casing; the colours are the site's, not
	// the interface's. Everything is sized in em off the frame's width.

	const PROBLEMS = ['bai1', 'bridge', 'egg', 'sum'];

	/** The problem the submission is for, as an index into PROBLEMS, and what it scores. */
	const SUBMITTED = 1;
	const SUBMITTED_MARKS = 20;

	/** Contestants in their final order; a score per problem, or null where nothing was submitted. */
	const RANKING: { name: string; face: string; scores: (number | null)[]; tones: string[] }[] = [
		{ name: 'Belikhun', face: 'pink', scores: [10, SUBMITTED_MARKS, 5, 20], tones: ['accepted', 'accepted', 'partial', 'accepted'] },
		{ name: 'thí sinh 1', face: 'blue', scores: [10, 20, null, 20], tones: ['accepted', 'accepted', 'none', 'accepted'] },
		{ name: 'thí sinh 2', face: 'lav', scores: [5, null, 5, 20], tones: ['partial', 'none', 'partial', 'accepted'] },
		{ name: 'thí sinh 3', face: 'grey', scores: [null, 0, 5, null], tones: ['none', 'failed', 'partial', 'none'] }
	];

	const LOGS = [
		{ problem: 'sum', result: '20 điểm', time: '18:07:12' },
		{ problem: 'egg', result: '5 điểm', time: '18:03:51' }
	];

	/** What the clock reads once the submission is judged, and how many seconds it runs through per card of scroll. */
	const CONTEST_SECONDS = 58 * 60 + 40;
	const CLOCK_RATE = 90;

	const RELOAD = 'M19 12a7 7 0 1 1-2.05-4.95M19 4v4h-4';

	let root = $state<HTMLDivElement>();
	let left = $state(CONTEST_SECONDS);
	let judged = $state(true);
	let earned = $state(SUBMITTED_MARKS);

	function total(scores: (number | null)[], index: number): string {
		const sum = scores.reduce<number>((all, score) => all + (score ?? 0), 0);

		return (index === 0
			? sum - SUBMITTED_MARKS + earned
			: sum
		).toFixed(2);
	}

	/** Where a row stands: the first two trade places when the submission is judged. */
	function place(index: number): number {
		if (judged || index > 1) {
			return index + 1;
		}

		return 2 - index;
	}

	function clock(seconds: number): string {
		return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
	}

	/**
	 * Follows one submission: the file is dropped, judged, lands in the ranking and lifts its row to the top.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 * @param shown the stretch of the timeline over which this card is on screen
	 */
	export function animate(timeline: gsap.core.Timeline, at: number, shown: Span): void {
		const scope = gsap.utils.selector(root!);
		const settled = at + 0.5;
		const judging = at + 0.26;
		const contest = { left: CONTEST_SECONDS, earned: 0 };
		const [mine, theirs] = scope('.row:not(.heading)');

		timeline
			// the clock and the reload arrows keep going for as long as the card is on screen
			.fromTo(
				contest,
				{ left: CONTEST_SECONDS + (settled - shown.from) * CLOCK_RATE },
				{
					left: CONTEST_SECONDS - (shown.to - settled) * CLOCK_RATE,
					duration: shown.to - shown.from,
					ease: 'none',
					onUpdate: () => {
						left = Math.round(contest.left);
						judged = timeline.time() >= judging;
					}
				},
				shown.from
			)
			.fromTo(scope('.reload'), { rotation: -360 }, { rotation: 360, duration: shown.to - shown.from, ease: 'none' }, shown.from)
			.from(scope('.panel'), { y: '1.5rem', autoAlpha: 0, duration: 0.06, stagger: 0.02, ease: 'power2.out' }, at)
			.from(scope('.file'), { y: '-4em', rotation: -14, autoAlpha: 0, duration: 0.08, ease: 'back.out(1.6)' }, at + 0.1)
			.fromTo(scope('.judge i'), { scaleX: 0 }, { scaleX: 1, duration: 0.08, ease: 'none' }, at + 0.18)
			.from(scope('.landed'), { scale: 0, autoAlpha: 0, duration: 0.05, ease: 'back.out(2.5)' }, judging)
			.fromTo(
				contest,
				{ earned: 0 },
				{
					earned: SUBMITTED_MARKS,
					duration: 0.08,
					ease: 'power1.out',
					onUpdate: () => {
						earned = Math.round(contest.earned);
					}
				},
				judging
			)
			// a quick trade of places: scrubbed slowly, the two rows would sit on top of each other
			.from(mine!, { y: '3em', duration: 0.03, ease: 'power2.inOut' }, judging + 0.06)
			.from(theirs!, { y: '-3em', duration: 0.03, ease: 'power2.inOut' }, judging + 0.06)
			.from(scope('.log.new'), { x: '2em', autoAlpha: 0, duration: 0.06, ease: 'power2.out' }, judging);

		judged = false;
		earned = 0;
	}
</script>

{#snippet head(title: string)}
	<h4>
		{title}
		<svg class="reload" viewBox="0 0 24 24" aria-hidden="true"><path d={RELOAD} /></svg>
	</h4>
{/snippet}

<div class="themis" bind:this={root}>
	<div class="column">
		<section class="panel time">
			{@render head('Thời gian')}
			<small>THỜI GIAN LÀM BÀI</small>
			<p class="clock">{clock(left)}</p>
			<span class="remaining"><i style:--left={left / 3600}></i></span>
			<p class="range"><span>01:15:00 tới 02:15:00</span><span>01:00:00</span></p>
		</section>

		<section class="panel submit">
			{@render head('Nộp bài')}
			<div class="drop">
				<b>THẢ TỆP TẠI ĐÂY</b>
				<small>hoặc</small>
				<span class="choose">Chọn tệp</span>

				<p class="file">
					<strong>{PROBLEMS[SUBMITTED]}.pas</strong>
					<span class="judge"><i></i></span>
				</p>
			</div>
		</section>
	</div>

	<div class="column">
		<section class="panel ranking">
			{@render head('Xếp hạng')}

			<p class="row heading">
				<span>#</span>
				<span class="who">Thí sinh</span>
				<span>Tổng</span>
				{#each PROBLEMS as problem (problem)}
					<span>{problem}</span>
				{/each}
			</p>

			{#each RANKING as row, index (row.name)}
				<p class="row place-{place(index)}">
					<span>{place(index)}</span>
					<span class="who"><i class="face {row.face}"></i>{row.name}</span>
					<span class="sum">{total(row.scores, index)}</span>
					{#each row.scores as score, problem (problem)}
						<span class="score {row.tones[problem]}">
							{#if score === null}
								×
							{:else if index === 0 && problem === SUBMITTED}
								<b class="landed">{score.toFixed(2)}</b>
							{:else}
								<b>{score.toFixed(2)}</b>
							{/if}
						</span>
					{/each}
				</p>
			{/each}
		</section>

		<section class="panel logs">
			{@render head('Nhật ký')}

			<p class="log new">
				<span><small>22/08/2019 18:10:44</small><strong>{PROBLEMS[SUBMITTED]}</strong></span>
				<span class="result">{SUBMITTED_MARKS} điểm<small>Pascal</small></span>
			</p>

			{#each LOGS as log (log.problem)}
				<p class="log">
					<span><small>22/08/2019 {log.time}</small><strong>{log.problem}</strong></span>
					<span class="result">{log.result}<small>Pascal</small></span>
				</p>
			{/each}
		</section>
	</div>
</div>

<style lang="scss">
	// the interface's roles, in the site's colours
	$text: var(--night);
	$muted: #8d86a8;
	$line: #ece8f5;
	$navy: var(--night);
	$green: var(--purple);
	$total: var(--purple);
	$accepted: #bfe8d0;
	$partial: var(--blue);
	$failed: var(--pink);

	.themis {
		display: grid;
		grid-template-columns: minmax(0, 0.72fr) minmax(0, 1fr);
		align-items: center;
		gap: 4%;

		@include below($bp-narrow) {
			grid-template-columns: minmax(0, 1fr);
			align-content: center;
		}
		height: 100%;
		min-height: 20rem;
		padding: 6%;
		border-radius: 1.5rem;
		background: linear-gradient(150deg, var(--lav), var(--purple));
		color: $text;
		overflow: hidden;
		container-type: inline-size;
	}

	// both columns are drawn at one size and scale with the frame
	.column {
		display: grid;
		gap: 1.4em;
		min-width: 0;
		font-size: clamp(0.5rem, 2.1cqw, 1.25rem);

		// on a phone only the clock and the ranking are kept, one above the other, at a size that reads
		@include below($bp-narrow) {
			font-size: 4.2cqw;
		}
		line-height: 1.3;
	}

	.submit,
	.logs {
		@include below($bp-narrow) {
			display: none;
		}
	}

	.panel {
		border-radius: 1em;
		background: #ffffff;
		box-shadow: 0 0.8em 2em rgba(42, 36, 64, 0.22);
		overflow: hidden;
	}

	h4 {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin: 0;
		padding: 0.8em 1.1em;
		border-bottom: 0.1em solid $line;
		color: $muted;
		font-family: var(--body);
		font-size: 0.9em;
		font-weight: 500;
		line-height: 1.3;
	}

	.reload {
		width: 1.2em;
		height: 1.2em;
		fill: none;
		stroke: $muted;
		stroke-width: 2;
		stroke-linecap: round;
		stroke-linejoin: round;
	}

	small {
		display: block;
		color: $muted;
		font-size: 0.7em;
	}

	.time {
		text-align: center;

		> small {
			margin-top: 1.4em;
			font-size: 0.8em;
			letter-spacing: 0.04em;
		}
	}

	.clock {
		color: $green;
		font-family: var(--display);
		font-size: 3.4em;
		font-weight: 800;
		font-variant-numeric: tabular-nums;
		line-height: 1.15;
	}

	.remaining {
		display: block;
		height: 0.3em;
		margin: 0.6em 1.1em 0;
		border-radius: 1em;
		background: $line;
		overflow: hidden;

		i {
			display: block;
			width: calc(var(--left) * 100%);
			height: 100%;
			background: $green;
		}
	}

	.range {
		display: flex;
		justify-content: space-between;
		padding: 0.4em 1.6em 1.1em;
		font-size: 0.7em;
		font-weight: 600;
	}

	.drop {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.3em;
		margin: 1em;
		padding: 1.4em 1em;
		border: 0.1em dashed var(--lav);
		border-radius: 0.6em;
		text-align: center;

		b {
			font-size: 0.9em;
		}
	}

	.choose {
		margin-top: 0.3em;
		padding: 0.5em 1.2em;
		border-radius: 2em;
		background: $navy;
		color: #ffffff;
		font-size: 0.8em;
		font-weight: 600;
	}

	// the dropped source file, lying on the box while it is judged
	.file {
		position: absolute;
		top: 64%;
		left: 68%;
		display: grid;
		gap: 0.5em;
		width: 8.5em;
		padding: 0.8em 1em;
		border-radius: 0.5em;
		background: $navy;
		color: #ffffff;
		font-family: var(--mono);
		font-size: 0.9em;
		text-align: left;
		translate: -50% -50%;
		rotate: -4deg;
		box-shadow: 0 0.6em 1.4em rgba(42, 36, 64, 0.4);
	}

	.judge {
		display: block;
		height: 0.3em;
		border-radius: 1em;
		background: rgba(255, 255, 255, 0.2);
		overflow: hidden;

		i {
			display: block;
			height: 100%;
			background: var(--pink);
			transform-origin: 0 50%;
		}
	}

	.row {
		display: grid;
		grid-template-columns: 2.2em minmax(0, 1fr) 3.8em repeat(4, 3.4em);
		align-items: stretch;
		height: 3em;
		font-size: 0.8em;

		> span {
			display: grid;
			place-items: center;
		}

		// on a phone the ranking keeps the first two problems only
		@include below($bp-narrow) {
			grid-template-columns: 2em minmax(0, 1fr) 3.6em repeat(2, 3em);
			padding-right: 0.8em;

			> :nth-child(n + 6) {
				display: none;
			}
		}

		&.heading {
			height: 2.4em;
			border-bottom: 0.1em solid $line;
			font-size: 0.7em;
			font-weight: 600;
		}

		&.place-1 {
			background: #f3effb;
		}

		> .who {
			display: flex;
			justify-content: start;
			gap: 0.6em;
			min-width: 0;
			font-weight: 600;
			white-space: nowrap;
		}
	}

	.sum {
		color: $total;
		font-weight: 700;
	}

	.score {
		color: #c5bfd8;

		b {
			color: $text;
			font-weight: 500;
		}

		&.accepted {
			background: $accepted;
		}

		&.partial {
			background: $partial;
		}

		&.failed {
			background: $failed;
		}
	}

	.face {
		flex: none;
		width: 2em;
		height: 2em;
		border-radius: 50%;
		background: #c5bfd8;

		&.pink {
			background: var(--pink);
		}

		&.blue {
			background: var(--blue);
		}

		&.lav {
			background: var(--lav);
		}
	}

	.log {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.5em 1em;
		border-bottom: 0.1em solid $line;
		font-size: 0.85em;

		strong {
			color: var(--purple);
		}

		&:last-child {
			border-bottom: 0;
		}
	}

	.result {
		font-weight: 600;
		text-align: right;
	}
</style>
