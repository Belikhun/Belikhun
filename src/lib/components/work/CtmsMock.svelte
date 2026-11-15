<!-- Copyright (c) 2026 Belikhun. Licensed under the MIT License.
     See LICENSE at the repository root. -->

<script lang="ts">
	import { gsap, type Span } from '#lib/motion/gsap.ts';

	// A few pieces of the schedule page, not the whole page: the navigation,
	// the week picker and the week's lessons as the phone layout draws them.
	// The labels are the app's own, so they stay in Vietnamese and in their own
	// casing; the lecturers' names are left out and the colours are the site's.
	// Everything is sized in em off the frame's width.

	const DAYS = [
		{ day: 'Thứ Năm', date: '13/10/2022', kind: 'Học trực tuyến', online: true, subject: 'An ninh và bảo mật dữ liệu', room: 'P51', time: '17:15 → 20:00', code: 'AAN5022022.008' },
		{ day: 'Thứ Sáu', date: '14/10/2022', kind: 'Học trực tuyến', online: true, subject: 'Nguyên lý hệ điều hành', room: 'O.01', time: '17:15 → 20:00', code: 'AAS6172022.005' },
		{ day: 'Thứ Bảy', date: '15/10/2022', kind: 'Học', online: false, subject: 'Phân tích và thiết kế hệ thống TT', room: 'P51', time: '07:30 → 11:15', code: 'AAS7182022.006', today: true }
	];

	/** The week the picker shows before and after it is stepped forward. */
	const LAST_WEEK = '03/10/2022';
	const THIS_WEEK = '10/10/2022';

	const CALENDAR = 'M4 5h16v16H4ZM4 10h16M8 3v4M16 3v4';

	/** The navigation icons, each a path on a 24 by 24 grid. */
	const TABS = [
		'M3 11 12 3l9 8v10h-6v-6H9v6H3Z',
		CALENDAR,
		'M4 20l1-5L16 4l4 4L9 19Z',
		'M4 4h16v16H4ZM9 16v-4M12 16V8M15 16v-6'
	];

	let root = $state<HTMLDivElement>();
	let week = $state(THIS_WEEK);

	/**
	 * Steps the picker forward a week, then lays that week's lessons out one by one.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 * @param shown the stretch of the timeline over which this card is on screen
	 */
	export function animate(timeline: gsap.core.Timeline, at: number, shown: Span): void {
		const scope = gsap.utils.selector(root!);
		const stepped = at + 0.1;

		timeline
			// the mark keeps turning for as long as the card is on screen; the picker's week is read off the same playhead
			.fromTo(
				scope('.mark'),
				{ rotation: -60 },
				{
					rotation: 60,
					duration: shown.to - shown.from,
					ease: 'none',
					onUpdate: () => {
						week = timeline.time() >= stepped
							? THIS_WEEK
							: LAST_WEEK;
					}
				},
				shown.from
			)
			.from(scope('.piece'), { y: '1.5rem', autoAlpha: 0, duration: 0.06, stagger: 0.02, ease: 'power2.out' }, at)
			.fromTo(scope('.skip'), { scale: 1 }, { scale: 0.88, duration: 0.02, repeat: 1, yoyo: true, ease: 'power1.inOut' }, stepped - 0.02)
			.from(scope('.day'), { x: '3em', autoAlpha: 0, duration: 0.08, stagger: 0.06, ease: 'power3.out' }, stepped + 0.02)
			.from(scope('.rail'), { scaleY: 0, duration: 0.06, stagger: 0.06, ease: 'none' }, stepped + 0.06)
			.from(scope('.done'), { scale: 0, duration: 0.04, stagger: 0.06, ease: 'back.out(3)' }, stepped + 0.12)
			.from(scope('.today'), { scale: 0, autoAlpha: 0, duration: 0.05, ease: 'back.out(3)' }, at + 0.4);

		week = LAST_WEEK;
	}
</script>

{#snippet icon(path: string)}
	<svg viewBox="0 0 24 24" aria-hidden="true"><path d={path} /></svg>
{/snippet}

<div class="ctms" bind:this={root}>
	<svg class="mark" viewBox="0 0 256 256" aria-hidden="true">
		<path d="M150 104a46 46 0 1 0 0 62" stroke-width="34" />
		<path d="M192 58v40M172 78h40" stroke-width="13" />
	</svg>

	<div class="controls">
		<p class="piece nav">
			<img src="/img/ctms/ctms-mark.svg" width="256" height="256" alt="" />
			<b>CTMS+</b>
			{#each TABS as tab, index (tab)}
				<i class:current={index === 1}>{@render icon(tab)}</i>
			{/each}
		</p>

		<h4 class="piece">{@render icon(CALENDAR)}lịch học</h4>

		<p class="piece field"><small>Ngày bắt đầu</small>{week}{@render icon(CALENDAR)}</p>

		<p class="piece buttons">
			<b class="view">{@render icon(CALENDAR)}Xem lịch</b>
			<b class="skip" aria-hidden="true">
				<svg viewBox="0 0 24 24"><path d="M11 5v14L2 12ZM22 5v14l-9-7Z" /></svg>
				<svg viewBox="0 0 24 24"><path d="M2 5v14l9-7ZM13 5v14l9-7Z" /></svg>
			</b>
		</p>
	</div>

	<div class="week">
		{#each DAYS as day (day.date)}
			<div class="day">
				<p class="when">
					<i class="dot" class:now={day.today}></i>
					<strong>{day.day}</strong>
					{day.date}
					{#if day.today}
						<span class="today">Hôm nay</span>
					{/if}
				</p>

				<i class="rail"></i>
				<i class="done"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 12.5l3.5 3.5L17 9" /></svg></i>

				<div class="slot">
					<p><span class="kind" class:online={day.online}>{day.kind}</span><b>{day.room}</b><b class="hours">{day.time}</b></p>
					<strong>{day.subject}</strong>
					<u>{day.code}</u>
				</div>
			</div>
		{/each}
	</div>
</div>

<style lang="scss">
	// the app's roles, in the site's colours
	$text: var(--night);
	$muted: #8d86a8;
	$sky: var(--purple);
	$plum: var(--night);
	$green: var(--purple);
	$link: var(--purple);

	.ctms {
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 0.7fr) minmax(0, 1fr);
		align-items: center;
		gap: 5%;

		@include below($bp-narrow) {
			grid-template-columns: minmax(0, 1fr);
			align-content: center;

			h4,
			.field,
			.buttons {
				display: none;
			}
		}
		height: 100%;
		min-height: 20rem;
		padding: 6%;
		border-radius: 1.5rem;
		background: linear-gradient(160deg, #cfe8f7, var(--blue) 70%);
		color: $text;
		overflow: hidden;
		isolation: isolate;
		container-type: inline-size;
	}

	.mark {
		position: absolute;
		z-index: -1;
		left: -16%;
		bottom: -34%;
		width: 62%;
		height: auto;
		fill: none;
		stroke: #ffffff;
		stroke-linecap: round;
		opacity: 0.3;
	}

	// both halves are drawn at one size and scale with the frame
	.controls,
	.week {
		display: grid;
		min-width: 0;
		font-size: clamp(0.5rem, 2.1cqw, 1.25rem);

		// on a phone only the navigation and the week are kept, one above the other, at a size that reads
		@include below($bp-narrow) {
			font-size: 4cqw;
		}
		line-height: 1.3;
	}

	.controls {
		gap: 1.2em;

		svg {
			flex: none;
			width: 1.3em;
			height: 1.3em;
			fill: none;
			stroke: currentColor;
			stroke-width: 2;
			stroke-linejoin: round;
		}
	}

	.nav {
		display: flex;
		align-items: center;
		gap: 0.9em;
		padding: 0.6em 0.9em;
		border-radius: 1em;
		background: #ffffff;
		box-shadow: 0 0.6em 1.6em rgba(42, 36, 64, 0.14);

		img {
			width: 1.8em;
			height: 1.8em;
		}

		b {
			margin-right: auto;
			font-weight: 700;
		}

		i {
			display: grid;
			padding-bottom: 0.3em;
			border-bottom: 0.2em solid transparent;
			color: $muted;

			&.current {
				border-color: $text;
				color: $text;
			}
		}
	}

	h4 {
		display: flex;
		align-items: center;
		gap: 0.4em;
		margin: 0.3em 0 0;
		font-family: var(--display);
		font-size: 2.2em;
		font-weight: 800;
		line-height: 1.1;
	}

	.field {
		display: grid;
		grid-template-columns: 1fr auto;
		align-items: center;
		padding: 0.7em 1.1em;
		border-radius: 1em;
		background: #ffffff;
		font-weight: 600;
		font-variant-numeric: tabular-nums;
		box-shadow: 0 0.6em 1.6em rgba(42, 36, 64, 0.14);

		svg {
			grid-row: 1 / 3;
			grid-column: 2;
		}

		small {
			color: $muted;
			font-size: 0.7em;
			font-weight: 600;
			letter-spacing: 0.04em;
			text-transform: uppercase;
		}
	}

	.buttons {
		display: flex;
		gap: 0.6em;

		b {
			display: flex;
			align-items: center;
			justify-content: center;
			gap: 0.5em;
			height: 3em;
			padding: 0 1.2em;
			border-radius: 2em;
			color: #ffffff;
			font-size: 0.85em;
			font-weight: 700;
			text-transform: uppercase;
		}
	}

	.view {
		flex: 1;
		background: $plum;
	}

	.skip {
		background: $sky;

		svg {
			fill: #ffffff;
			stroke: none;
		}
	}

	.week {
		gap: 1.2em;
	}

	.day {
		position: relative;
		display: grid;
		gap: 0.5em;
		padding-left: 1.8em;
	}

	.when {
		display: flex;
		align-items: center;
		gap: 0.4em;
		margin-left: -1.8em;
	}

	.dot {
		flex: none;
		width: 1em;
		height: 1em;
		margin-right: 0.4em;
		border-radius: 50%;
		background: $green;

		&.now {
			background: #d77fae;
		}
	}

	.today {
		margin-left: 0.4em;
		padding: 0.1em 0.8em;
		border-radius: 1em;
		background: var(--pink);
		font-size: 0.7em;
		font-weight: 700;
		text-transform: uppercase;
	}

	// the line that ties a day to its lesson, ending in the tick of a lesson already attended
	.rail {
		position: absolute;
		top: 1.8em;
		bottom: 2em;
		left: 0.4em;
		width: 0.2em;
		background: $green;
		transform-origin: 50% 0;
	}

	.done {
		position: absolute;
		bottom: 0.6em;
		left: 0;
		display: grid;
		place-items: center;
		width: 1em;
		height: 1em;
		border-radius: 50%;
		background: $green;

		svg {
			width: 0.8em;
			height: 0.8em;
			fill: none;
			stroke: #ffffff;
			stroke-width: 3.5;
			stroke-linecap: round;
			stroke-linejoin: round;
		}
	}

	.kind {
		padding: 0.1em 0.8em;
		border-radius: 1em;
		background: #bfe8d0;
		font-size: 0.85em;
		text-transform: uppercase;

		&.online {
			background: var(--blue);
		}
	}

	// not `.card`: the work stack looks its own cards up by that name
	.slot {
		display: grid;
		gap: 0.3em;
		padding: 0.8em 1em;
		border-radius: 1em;
		background: #ffffff;
		box-shadow: 0 0.6em 1.6em rgba(42, 36, 64, 0.14);

		p {
			display: flex;
			align-items: center;
			gap: 0.8em;
			font-size: 0.8em;
			font-weight: 700;
		}

		> strong {
			font-size: 1.3em;
			font-weight: 700;
			line-height: 1.2;
		}

		u {
			color: $link;
			font-size: 0.75em;
		}
	}

	.hours {
		margin-left: auto;
	}
</style>
