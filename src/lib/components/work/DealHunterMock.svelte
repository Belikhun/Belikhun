<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { picture } from '#lib/content/site.ts';
	import { gsap, type Span } from '#lib/motion/gsap.ts';

	// Two views of the extension's window, not the whole thing: the list of
	// scripts for the page being watched, and one script running. A flash sale
	// is followed through them: the script is picked, waits for midnight, and
	// orders the moment the price drops. The labels are the interface's own, so
	// they stay in Vietnamese and in their own casing; the shop and the item are
	// made up, and the colours are the site's. Everything is sized in em off the
	// frame's width.

	const SCRIPTS = [
		{ id: 'flashSale', name: 'Flash Sale Hunter', about: 'Tự đặt mua khi giá giảm tới mức đã đặt', version: 'v012', tone: 'pink' },
		{ id: 'voucher', name: 'Voucher Collector', about: 'Thu thập toàn bộ mã giảm giá trên trang', version: 'v004', tone: 'blue' },
		{ id: 'tracker', name: 'Price Tracker', about: 'Theo dõi giá sản phẩm theo thời gian', version: 'v007', tone: 'lav' }
	];

	/** Where in SCRIPTS the ones that run on any page start; those before it are for the page being watched. */
	const ANY_PAGE_FROM = 2;

	const TAGS = ['Flash Sale', 'Freeship', 'Mall'];

	const PRICE = '1.290.000';
	const SALE_PRICE = '199.000';

	/** Seconds of the wait the progress bar covers, how often the script checks the price, and how many checks the log keeps. */
	const WAIT_SECONDS = 20;
	const CHECKS_PER_SECOND = 4;
	const LOG_LINES = 2;

	/** Seconds the window's clock runs through per card of scroll. */
	const CLOCK_RATE = 40;

	const DAY_SECONDS = 86400;

	/** The extension's own logo, in the site's colours. */
	const LOGO = picture('hunter/icon.webp', '').src;

	const RELOAD = 'M19 12a7 7 0 1 1-2.05-4.95M19 4v4h-4';
	const SEARCH = 'M10.5 4a6.5 6.5 0 1 0 0 13a6.5 6.5 0 0 0 0-13zM15.5 15.5L20 20';
	const NETWORK = 'M9 4h6v5H9zM3 15h6v5H3zM15 15h6v5h-6zM12 9v3M6 15v-3h12v3';

	let root = $state<HTMLDivElement>();

	/** Seconds past midnight, when the sale opens: negative while the script is still waiting. */
	let since = $state(12);

	const left = $derived(Math.max(-since, 0));
	const bought = $derived(since >= 0);
	const checks = $derived(Math.max(Math.floor((WAIT_SECONDS - left) * CHECKS_PER_SECOND), 1));

	/** The newest checks, oldest first; the order takes the last line once it is placed. */
	const lines = $derived.by(() => {
		const kept = bought
			? LOG_LINES - 1
			: LOG_LINES;

		return Array.from({ length: kept }, (_, index) => checks - kept + 1 + index).filter((check) => check > 0);
	});

	function pad(value: number, length = 2): string {
		return String(Math.floor(value)).padStart(length, '0');
	}

	function clock(seconds: number): string {
		const time = (DAY_SECONDS + Math.floor(seconds)) % DAY_SECONDS;

		return `${pad(time / 3600)}:${pad((time % 3600) / 60)}:${pad(time % 60)}`;
	}

	function millis(seconds: number): string {
		return pad((((seconds % 1) + 1) % 1) * 1000, 3);
	}

	/**
	 * Follows one flash sale: the script is picked from the list, counts down to midnight and orders when the price drops.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 * @param shown the stretch of the timeline over which this card is on screen
	 */
	export function animate(timeline: gsap.core.Timeline, at: number, shown: Span): void {
		const scope = gsap.utils.selector(root!);
		const midnight = at + 0.4;
		const sale = { since: 0 };

		timeline
			// the clock and the reload arrows keep going for as long as the card is on screen
			.fromTo(
				sale,
				{ since: (shown.from - midnight) * CLOCK_RATE },
				{
					since: (shown.to - midnight) * CLOCK_RATE,
					duration: shown.to - shown.from,
					ease: 'none',
					onUpdate: () => {
						since = sale.since;
					}
				},
				shown.from
			)
			.fromTo(scope('.reload'), { rotation: -360 }, { rotation: 360, duration: shown.to - shown.from, ease: 'none' }, shown.from)
			// the list is there from the start; the running script arrives once its entry is pressed
			.fromTo(scope('.script.picked'), { scale: 1 }, { scale: 0.94, duration: 0.03, repeat: 1, yoyo: true, ease: 'power2.inOut' }, at + 0.12)
			.from(scope('.running'), { y: '2rem', autoAlpha: 0, duration: 0.08, ease: 'power2.out' }, at + 0.16)
			.from(scope('.running > :not(.top, .proxy)'), { y: '1.5em', autoAlpha: 0, duration: 0.06, stagger: 0.02, ease: 'power2.out' }, at + 0.18)
			.from(scope('.stamp'), { scale: 0, rotation: -24, autoAlpha: 0, duration: 0.06, ease: 'back.out(2.5)' }, midnight)
			.fromTo(scope('.price'), { scale: 1.3 }, { scale: 1, duration: 0.06, ease: 'power2.out', immediateRender: false }, midnight);

		since = sale.since;
	}
</script>

{#snippet icon(path: string, name: string)}
	<svg class={name} viewBox="0 0 24 24" aria-hidden="true"><path d={path} /></svg>
{/snippet}

<!-- the top of every screen: the bar with its clock, and the proxy strip under it -->
{#snippet top()}
	<header class="top">
		<img class="mark" src={LOGO} width="256" height="256" alt="" />
		<span class="clock"><sub>Th6</sub> {clock(since)}<small>.{millis(since)}</small></span>
		<b>Belikhun</b>
		<span class="badge">Admin</span>
		<span class="menu"><i></i><i></i><i></i></span>
	</header>

	<p class="proxy">
		{@render icon(NETWORK, 'network')}
		<span class="count"><b>3 PROXY</b><small>3 proxy đang hoạt động</small></span>
		<span class="state">IDLE</span>
		<span class="again">{@render icon(RELOAD, 'reload')}</span>
	</p>
{/snippet}

{#snippet entry(script: (typeof SCRIPTS)[number], picked: boolean)}
	<p class="script" class:picked>
		<i class="face {script.tone}"></i>
		<span class="about"><b>{script.name}</b>{script.about}</span>
		<span class="build">{script.id}<br />{script.version}</span>
	</p>
{/snippet}

<div class="hunter" bind:this={root}>
	<section class="window listing">
		{@render top()}

		<div class="page">
			<b>SHOP.EXAMPLE</b>
			<span>Tai nghe không dây X2 | Flash Sale 0h</span>
			<small>Đang theo dõi TabID: 1042</small>
			{@render icon(RELOAD, 'reload')}
		</div>

		<p class="search">nhập để tìm kiếm {@render icon(SEARCH, 'glass')}</p>

		<h4>TRANG HIỆN TẠI</h4>

		{#each SCRIPTS.slice(0, ANY_PAGE_FROM) as script, index (script.id)}
			{@render entry(script, index === 0)}
		{/each}

		<h4>CHẠY NGOÀI</h4>

		{#each SCRIPTS.slice(ANY_PAGE_FROM) as script (script.id)}
			{@render entry(script, false)}
		{/each}
	</section>

	<section class="window running">
		{@render top()}

		<h4>NHẬT KÍ CHẠY: <i>flashSale</i></h4>

		<div class="item">
			<small>#SP-204815</small>
			<b>Tai nghe không dây X2</b>
			<span class="price" class:dropped={bought}>{bought ? SALE_PRICE : PRICE}<sub>đ</sub></span>

			<span class="tags">
				{#each TAGS as tag (tag)}
					<span>{tag}</span>
				{/each}
			</span>

			<span class="stamp">-85%</span>
		</div>

		<ol class="log">
			<li><span>1</span>Giá đặt mua: {SALE_PRICE}đ</li>
			<li class="group"><span>▾</span>Kiểm tra giá</li>

			{#each lines as check (check)}
				<li class="nested"><span>{check}</span>check #{check} · {PRICE}đ</li>
			{/each}

			{#if bought}
				<li class="nested done"><span>{checks + 1}</span>Đã đặt mua · {SALE_PRICE}đ</li>
			{/if}
		</ol>

		<div class="status">
			<small>{bought ? 'ĐẶT MUA THÀNH CÔNG' : 'ĐANG CHỜ GIÁ GIẢM'}</small>
			<i class="beat" class:done={bought}></i>
			<span class="cancel">Hủy</span>
			<span class="timer">00:{pad(left)}<small>.{pad((left % 1) * 1000, 3)}</small></span>
			<span class="track"><i style:scale="{Math.min(1 - left / WAIT_SECONDS, 1)} 1"></i></span>
			<p class="range"><span>{clock(Math.min(since, 0))}</span><span>00:00:00</span></p>

			<p class="prices">
				<b class="current">{bought ? SALE_PRICE : PRICE}đ</b>
				<span>/</span>
				<b class="target">{SALE_PRICE}đ</b>
				<b class="saved">-85%</b>
			</p>

			<p class="detail"><b>{bought ? 'ĐÃ ĐẶT MUA' : 'CÒN HÀNG'}</b><span>check #{checks} · 38ms · proxy 2</span></p>
		</div>
	</section>
</div>

<style lang="scss">
	// the extension's dark window, in the site's colours
	$window: var(--night);
	$text: #ece8f7;
	$muted: #a39cbd;
	$panel: #3a3259;
	$rule: #4a4170;

	.hunter {
		// one cell for both windows: the list sits behind, the running script in front of its right side
		display: grid;
		height: 100%;
		min-height: 20rem;
		padding: 4%;
		border-radius: 1.5rem;
		background: linear-gradient(150deg, var(--blue), var(--purple) 55%, var(--night));
		overflow: hidden;
		container-type: inline-size;

	}

	// both windows are drawn at one size and scale with the frame
	.window {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		grid-area: 1 / 1;
		gap: 0.5em;
		width: 28.5em;
		padding: 0.7em;
		border-radius: 1em;
		background: $window;
		color: $text;
		font-size: clamp(0.5rem, 1.95cqw, 1.25rem);
		line-height: 1.3;
		box-shadow: 0 1.5em 3em rgba(42, 36, 64, 0.35);

		// on a phone only the running script is kept, at a size that reads
		@include below($bp-narrow) {
			width: auto;
			font-size: 3.6cqw;
		}

		svg {
			fill: none;
			stroke: currentColor;
			stroke-width: 2.4;
			stroke-linecap: round;
			stroke-linejoin: round;
		}

		h4 {
			margin: 0;
			padding: 0.3em 0.8em;
			border-radius: 0.4em;
			background: $panel;
			color: $muted;
			font-size: 0.85em;
			font-weight: 700;

			i {
				color: $text;
			}
		}
	}

	.listing {
		place-self: start start;

		@include below($bp-narrow) {
			display: none;
		}
	}

	.running {
		place-self: end end;

		@include below($bp-narrow) {
			place-self: center stretch;
		}
	}

	.top {
		display: flex;
		align-items: center;
		gap: 0.6em;
	}

	.mark {
		width: 2em;
		height: 2em;
	}

	.clock {
		margin-right: auto;
		font-family: var(--mono);
		font-size: 1.15em;
		font-weight: 600;
		font-variant-numeric: tabular-nums;
		white-space: nowrap;

		sub {
			font-family: var(--body);
			font-size: 0.6em;
			font-weight: 400;
		}

		small {
			font-size: 0.7em;
		}
	}

	.badge {
		padding: 0.1em 0.7em;
		border-radius: 1em;
		background: var(--pink);
		color: var(--night);
		font-weight: 600;
	}

	.menu {
		display: grid;
		gap: 0.25em;
		width: 1.4em;

		i {
			height: 0.2em;
			border-radius: 0.2em;
			background: currentColor;
		}
	}

	// the count on the left, the state and the reload button on the right
	.proxy {
		display: flex;
		align-items: center;
		gap: 0.6em;
		padding-left: 0.7em;
		border-radius: 0.6em;
		background: linear-gradient(90deg, var(--blue), var(--lav));
		color: var(--night);
		overflow: hidden;

		.network {
			width: 1.5em;
		}

		.count {
			display: grid;
			margin-right: auto;
			line-height: 1.15;

			small {
				font-size: 0.7em;
			}
		}

		.state {
			font-family: var(--mono);
			font-weight: 600;
		}

		.again {
			display: grid;
			place-items: center;
			align-self: stretch;
			width: 2.6em;
			padding-block: 0.6em;
			background: var(--purple);
			color: #ffffff;

			svg {
				width: 1.2em;
			}
		}
	}

	.search {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding-inline: 0.3em;
		color: $rule;
		font-size: 1.4em;
		font-weight: 600;

		svg {
			width: 1em;
			color: $muted;
		}
	}

	.page,
	.item {
		position: relative;
		display: grid;
		gap: 0.2em;
		padding: 0.7em 1em;
		border-radius: 0.8em;
		background: $panel;
	}

	.page {
		b {
			font-size: 1.3em;
		}

		svg {
			position: absolute;
			top: 50%;
			right: 1em;
			width: 1.3em;
			color: $muted;
			translate: 0 -50%;
		}

		small {
			color: $muted;
		}
	}

	.script {
		display: flex;
		align-items: center;
		gap: 0.8em;
		padding: 0.3em 0.5em;
		border-radius: 0.8em;

		&.picked {
			background: color-mix(in srgb, var(--lav) 22%, transparent);
		}
	}

	.face {
		flex: none;
		width: 2.4em;
		height: 2.4em;
		border-radius: 50%;

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

	.about {
		flex: 1;
		min-width: 0;
		color: $muted;
		font-size: 0.9em;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;

		b {
			display: block;
			color: $text;
			font-size: 1.2em;
		}
	}

	.build {
		color: $muted;
		font-family: var(--mono);
		font-size: 0.8em;
		text-align: right;
	}

	.item {
		justify-items: center;
		text-align: center;

		small {
			color: $muted;
			font-family: var(--mono);
		}

		b {
			font-size: 1.2em;
		}
	}

	.price {
		color: var(--blue);
		font-size: 2em;
		font-weight: 700;
		line-height: 1.1;

		&.dropped {
			color: var(--pink);
		}

		sub {
			font-size: 0.55em;
		}
	}

	.tags {
		display: flex;
		gap: 0.5em;
		margin-top: 0.3em;

		span {
			padding: 0.1em 0.8em;
			border-radius: 1em;
			background: $text;
			color: var(--night);
			font-size: 0.85em;
		}
	}

	.stamp {
		position: absolute !important;
		top: 0.5em;
		right: 0.5em;
		padding: 0.2em 0.6em;
		border-radius: 0.6em;
		background: var(--pink);
		color: var(--night);
		font-weight: 700;
		rotate: 8deg;
	}

	.log {
		display: grid;
		gap: 0.1em;
		min-height: 5.6em;
		align-content: start;
		font-family: var(--mono);
		font-size: 0.95em;

		li {
			display: flex;
			gap: 0.8em;
		}

		span {
			flex: none;
			width: 2.6em;
			padding-right: 0.8em;
			border-right: 0.1em solid $rule;
			color: $muted;
			text-align: right;
		}

		.group span {
			border-right-color: transparent;
		}

		.nested span {
			width: 4.6em;
		}

		.done {
			color: var(--pink);
			font-weight: 700;
		}
	}

	.status {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto auto;
		align-items: center;
		gap: 0.2em 0.8em;
		padding-top: 0.5em;
		border-top: 0.1em solid $rule;

		> small {
			color: $muted;
			font-weight: 700;
		}
	}

	.beat {
		width: 0.8em;
		height: 0.8em;
		border-radius: 50%;
		background: var(--blue);

		&.done {
			background: var(--pink);
		}
	}

	.cancel {
		grid-row: span 2;
		padding: 0.4em 1.2em;
		border-radius: 0.4em;
		background: var(--lav);
		color: var(--night);
		font-weight: 700;
	}

	.timer {
		grid-column: 1 / span 2;
		font-family: var(--mono);
		font-size: 2.2em;
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		line-height: 1;

		small {
			font-size: 0.55em;
		}
	}

	.track {
		grid-column: 1 / -1;
		height: 0.6em;
		margin-top: 0.3em;
		border-radius: 0.6em;
		background: $panel;
		overflow: hidden;

		i {
			display: block;
			height: 100%;
			background: linear-gradient(90deg, var(--purple), var(--blue));
			transform-origin: 0 50%;
		}
	}

	.range,
	.detail {
		grid-column: 1 / -1;
		display: flex;
		justify-content: space-between;
		color: $muted;
		font-size: 0.8em;
		font-variant-numeric: tabular-nums;
	}

	.detail b {
		color: $text;
	}

	.prices {
		grid-column: 1 / -1;
		display: flex;
		gap: 0.6em;
		font-size: 1.1em;

		.current {
			color: var(--blue);
		}

		.target {
			color: var(--pink);
		}

		.saved {
			margin-left: auto;
			color: var(--lav);
		}
	}
</style>
