<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onDestroy } from 'svelte';

	import { gsap, type Span } from '#lib/motion/gsap.ts';

	// A few pieces of the smart home project, not the whole page: two dashboard
	// blocks, one quick switch, a drawing of one of the boards, and the chat
	// panel of the assistant, Bụt. Their look follows the project's own
	// stylesheet (iot-smart-server/public/styles.scss). The labels and the
	// conversation are the app's own, so they stay in Vietnamese. Everything is
	// sized in em off the frame's width.

	/** The breadboard's rows of holes, as y positions on the drawing. */
	const HOLE_ROWS = [30, 39, 48, 57, 66, 84, 93, 102, 111, 120];

	/** The header pins down each side of the ESP32, as y positions on the drawing. */
	const PINS = [50, 58, 66, 74, 82, 90, 98, 106];

	/** Gauges sweep this much of a circle of radius 40, in degrees and in path length. */
	const SWEEP = 260;
	const CIRCLE = 2 * Math.PI * 40;
	const ARC = CIRCLE * (SWEEP / 360);

	const ROOM_TEMPERATURE = 31;
	const COOLED_TEMPERATURE = 27;
	const FAN_SPEED = 80;

	/** How loud each slice of the spoken request was, from silence to full, as the recorder would report it. */
	const LOUDNESS = [
		0.12, 0.3, 0.62, 0.85, 0.5, 0.74, 0.92, 0.6, 0.28, 0.14, 0.45, 0.8, 0.96, 0.7, 0.52, 0.86,
		0.64, 0.34, 0.18, 0.56, 0.9, 0.72, 0.44, 0.66, 0.38, 0.2, 0.12, 0.08
	];

	/** How long the spoken request lasts on the recorder's timer, in seconds. */
	const SPOKEN_SECONDS = 3;

	/** How fast the propeller turns at full speed, in degrees a second. */
	const FULL_SPIN = 900;

	let root = $state<HTMLDivElement>();
	let temperature = $state(COOLED_TEMPERATURE);
	let fanSpeed = $state(FAN_SPEED);

	let recording = $state(false);
	let heard = $state(0);

	let stopSpinning: (() => void) | undefined;

	/** The dash pattern that fills a share of the sweep. */
	function fill(share: number): string {
		return `${Math.max(0, Math.min(1, share)) * ARC} ${CIRCLE}`;
	}

	/**
	 * Plays one request: the visitor says they feel hot, the assistant switches
	 * the fan on, and the room cools.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 * @param _shown unused: the fan keeps this card moving on its own clock
	 */
	export function animate(timeline: gsap.core.Timeline, at: number, _shown: Span): void {
		const scope = gsap.utils.selector(root!);
		const room = { temperature: ROOM_TEMPERATURE, fanSpeed: 0 };

		// the request is spoken first; the fan is switched when the assistant's call lands
		const spoken = { from: at + 0.04, to: at + 0.14 };
		const switched = at + 0.22;
		const voice = { heard: 0 };

		timeline
			.from(scope('.block, .switch, .board'), { y: '1.5rem', autoAlpha: 0, duration: 0.06, stagger: 0.025, ease: 'power2.out' }, at)
			.fromTo(
				voice,
				{ heard: 0 },
				{
					heard: 1,
					duration: spoken.to - spoken.from,
					ease: 'none',
					onUpdate: () => {
						heard = voice.heard;
					}
				},
				spoken.from
			)
			// scrubbing runs both ways, so whether the microphone is open is read off the playhead
			.to({}, {
				duration: 0.5,
				onUpdate: () => {
					const now = timeline.time();

					recording = now >= spoken.from && now < spoken.to;
				}
			}, at)
			.from(scope('.message'), { y: '0.75rem', autoAlpha: 0, duration: 0.06, stagger: 0.08, ease: 'power2.out' }, spoken.to)
			.fromTo(
				room,
				{ fanSpeed: 0 },
				{
					fanSpeed: FAN_SPEED,
					duration: 0.06,
					ease: 'power2.out',
					onUpdate: () => {
						fanSpeed = Math.round(room.fanSpeed);
					}
				},
				switched
			)
			.fromTo(
				room,
				{ temperature: ROOM_TEMPERATURE },
				{
					temperature: COOLED_TEMPERATURE,
					duration: 0.2,
					ease: 'none',
					onUpdate: () => {
						temperature = Math.round(room.temperature * 10) / 10;
					}
				},
				switched + 0.03
			);

		temperature = ROOM_TEMPERATURE;
		fanSpeed = 0;

		// The propeller runs on its own clock for as long as the fan is on, at the
		// speed the dial shows; scrolling only sets that speed.
		const propeller = scope('.prop');
		let angle = 0;

		const spin = (_time: number, deltaMs: number): void => {
			if (fanSpeed === 0) {
				return;
			}

			angle = (angle + (fanSpeed / 100) * FULL_SPIN * (deltaMs / 1000)) % 360;
			// turned about the motor's shaft, given in the drawing's own coordinates
			gsap.set(propeller, { rotation: angle, svgOrigin: '60 61' });
		};

		gsap.ticker.add(spin);
		stopSpinning = () => gsap.ticker.remove(spin);
	}

	onDestroy(() => stopSpinning?.());
</script>

<div class="home" bind:this={root}>
	<div class="devices">
		<section class="block fan">
			<p class="blade">Quạt</p>
			<div class="gauge">
				<svg viewBox="0 0 100 86" aria-hidden="true">
					<circle class="track" cx="50" cy="50" r="40" stroke-dasharray={fill(1)} />
					<circle class="value" cx="50" cy="50" r="40" stroke-dasharray={fill(fanSpeed / 100)} />
				</svg>
				<p><b>{fanSpeed}%</b></p>
			</div>
		</section>

		<section class="block heat">
			<p class="blade">Nhiệt độ</p>
			<div class="gauge">
				<svg viewBox="0 0 100 86" aria-hidden="true">
					<circle class="track" cx="50" cy="50" r="40" stroke-dasharray={fill(1)} />
					<circle class="value" cx="50" cy="50" r="40" stroke-dasharray={fill(temperature / 50)} />
				</svg>
				<p><b>{temperature.toFixed(1)}</b>°C</p>
			</div>
		</section>

		<p class="switch" class:on={fanSpeed > 0}>
			<svg viewBox="0 0 24 24" aria-hidden="true">
				<path d="M12 12C8 4 15 1 17 5S13 11 12 12ZM12 12C20 8 23 15 19 17S13 13 12 12ZM12 12C16 20 9 23 7 19S11 13 12 12ZM12 12C4 16 1 9 5 7S11 11 12 12Z" />
			</svg>
			<span><b>Quạt phòng khách</b>{fanSpeed > 0 ? 'Bật' : 'Tắt'}</span>
		</p>

		<svg class="board" class:on={fanSpeed > 0} viewBox="0 0 240 150" role="img" aria-label="a drawing of an ESP32 on a breadboard, wired to a small fan and a buzzer">
			<rect class="bread" width="240" height="150" rx="8" />
			<path class="rail" d="M10 14H230M10 136H230" />

			{#each HOLE_ROWS as y (y)}
				<path class="holes" d="M14 {y}H228" />
			{/each}

			<path class="wire red" d="M150 44C170 22 192 22 202 46" />
			<path class="wire blue" d="M62 84C62 108 96 112 108 98" />
			<path class="wire yellow" d="M150 98C170 112 188 108 198 92" />

			<rect class="chip" x="104" y="40" width="46" height="78" rx="3" />
			<rect class="shield" x="110" y="44" width="34" height="30" rx="2" />
			<rect class="port" x="120" y="112" width="14" height="10" rx="1.5" />
			<circle class="led" cx="114" cy="86" r="2.5" />

			{#each PINS as y (y)}
				<path class="pin" d="M100 {y}H104M150 {y}H154" />
			{/each}

			<circle class="buzzer" cx="200" cy="80" r="13" />
			<circle class="buzzer-hole" cx="200" cy="80" r="3" />

			<rect class="motor" x="50" y="48" width="20" height="26" rx="3" />
			<g class="prop">
				<path d="M60 61C40 48 36 32 46 28S66 46 60 61ZM60 61C80 74 84 90 74 94S54 76 60 61Z" />
				<circle cx="60" cy="61" r="5" />
			</g>
		</svg>
	</div>

	<div class="chat">
		<p class="welcome">Xin chào! Tôi là <strong>Bụt</strong>, trợ lý ảo nhà thông minh của bạn!</p>

		<p class="message user">tôi đang cảm thấy nóng</p>
		<p class="message call"><i></i><span>Thực thi thành công<code>setDeviceFeatureValues()</code></span></p>
		<p class="message reply">Quạt phòng khách đã được bật lên. Hy vọng bạn sẽ cảm thấy mát hơn!</p>

		<div class="ask" class:recording>
			{#if recording}
				<p class="waveform" aria-hidden="true">
					<span class="timer">00:0{Math.floor(heard * SPOKEN_SECONDS)}</span>
					<span class="bars">
						{#each LOUDNESS.slice(0, Math.ceil(heard * LOUDNESS.length)) as loudness, index (index)}
							<i style:--loudness="{loudness * 100}%"></i>
						{/each}
					</span>
				</p>
			{:else}
				<p class="textbox">Bạn muốn làm gì...</p>
			{/if}

			<span class="voice">
				<svg viewBox="0 0 24 24" aria-hidden="true">
					{#if recording}
						<rect x="7" y="7" width="10" height="10" rx="2" />
					{:else}
						<rect x="9" y="3" width="6" height="11" rx="3" />
						<path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21" />
					{/if}
				</svg>
			</span>
		</div>
	</div>
</div>

<style lang="scss">
	// the project's own tokens
	$background-1: #f5f5f5;
	$background-2: #eeeeee;
	$text: rgb(32, 30, 30);
	$border: rgba(82, 109, 130, 0.2);
	$accent: #3f4db8;
	$green: #55b400;
	$orange: #ff4d0d;

	.home {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		align-items: center;
		gap: 5%;

		@include below($bp-narrow) {
			grid-template-columns: minmax(0, 1fr);

			padding-block: 8%;

			.board {
				display: none;
			}
		}
		height: 100%;
		min-height: 20rem;
		padding: 6%;
		border-radius: 1.5rem;
		// a deeper pink than the stage behind the card, so the panel reads as a panel
		background: linear-gradient(160deg, #f4cfe2, #e3a2c6);
		color: $text;
		overflow: hidden;
		container-type: inline-size;
	}

	// both halves are drawn at one size and scale with the frame
	.devices,
	.chat {
		font-size: clamp(0.5rem, 2.1cqw, 1.25rem);

		// on a phone the two halves stack, at a size that reads
		@include below($bp-narrow) {
			font-size: 4cqw;
		}
		line-height: 1.35;
	}

	.devices {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 1em;
	}

	.block {
		display: grid;
		justify-items: center;
		gap: 0.4em;
		padding-bottom: 1em;
		border: 0.1em solid $border;
		border-radius: 1em;
		background: #ffffff;
		box-shadow: rgba(75, 75, 75, 0.12) -0.25em 0.5em 1.15em 0.2em;
		overflow: hidden;
	}

	.blade {
		justify-self: start;
		min-width: 5em;
		padding: 0.45em 1em;
		border-bottom-right-radius: 1em;
		background: $green;
		color: #ffffff;
		font-size: 0.65em;
		font-weight: 600;

		.heat & {
			background: $orange;
		}
	}

	.gauge {
		position: relative;
		display: grid;
		justify-items: center;
		width: 72%;

		svg {
			width: 100%;
			height: auto;
			overflow: visible;
		}

		circle {
			fill: none;
			stroke-width: 9;
			stroke-linecap: round;
			// the sweep opens downwards: it starts at the lower left and ends at the lower right
			transform: rotate(140deg);
			transform-origin: 50px 50px;
		}

		.track {
			stroke: $background-2;
		}

		.value {
			stroke: $green;

			.heat & {
				stroke: $orange;
			}
		}

		p {
			position: absolute;
			top: 40%;
			font-size: 0.75em;
			font-weight: 600;
		}

		b {
			font-size: 1.4em;
			font-weight: 700;
			font-variant-numeric: tabular-nums;
		}
	}

	.switch {
		grid-column: 1 / -1;
		display: flex;
		align-items: center;
		gap: 0.8em;
		padding: 0.8em 1.4em;
		border-radius: 2em;
		background: #ffffff;
		font-size: 0.85em;
		line-height: 1.25;
		box-shadow: rgba(75, 75, 75, 0.12) -0.25em 0.5em 1.15em 0.2em;

		svg {
			flex: none;
			width: 1.6em;
			height: 1.6em;
			fill: currentColor;
		}

		span {
			display: grid;
		}

		b {
			font-weight: 600;
		}

		&.on {
			background: $orange;
			color: #ffffff;
		}
	}

	// the assistant's panel, as it floats over the dashboard
	.chat {
		display: grid;
		// a fixed track: the waveform's bars must be clipped by the box, never widen the panel
		grid-template-columns: minmax(0, 1fr);
		align-content: start;
		gap: 0.7em;
		padding: 1.4em;
		border: 0.1em solid $border;
		border-radius: 2em;
		background: #ffffff;
		box-shadow: rgba(0, 0, 0, 0.16) -0.25em 0.5em 1.75em -0.5em;
	}

	.welcome {
		padding: 0 0.4em 0.6em;
		font-size: 1.1em;
		font-weight: 600;
		text-align: center;

		strong {
			background: linear-gradient(160deg, #04b241 0%, #09b1f3 50%, #f94569 100%);
			background-clip: text;
			color: transparent;
		}
	}

	.ask {
		display: flex;
		align-items: center;
		gap: 0.8em;
		min-width: 0;
		margin-top: 1.2em;
	}

	.textbox,
	.waveform {
		display: flex;
		align-items: center;
		flex: 1;
		gap: 0.8em;
		min-width: 0;
		height: 2.6em;
		padding: 0 1em;
		border-radius: 3em;
		background: $background-1;
		color: rgb(99, 92, 92);
		font-size: 0.85em;
	}

	// while the microphone is open the box turns into the recorder: a timer and the loudness of each slice
	.waveform {
		background: $accent;
		color: #ffffff;
		overflow: hidden;
	}

	.timer {
		display: flex;
		align-items: center;
		gap: 0.5em;
		font-weight: 600;
		font-variant-numeric: tabular-nums;

		&::before {
			content: '';
			width: 0.5em;
			height: 0.5em;
			border-radius: 50%;
			background: rgb(255, 110, 110);
		}
	}

	// new bars arrive at the right edge and push the older ones left, as in the app
	.bars {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		flex: 1;
		gap: 0.25em;
		height: 100%;
		min-width: 0;
		overflow: hidden;

		i {
			flex: none;
			width: 0.25em;
			height: var(--loudness);
			min-height: 0.125em;
			max-height: 80%;
			border-radius: 0.5em;
			background: #ffffff;
			animation: swell 0.3s cubic-bezier(0.87, 0, 0.13, 1) backwards;
		}
	}

	@keyframes swell {
		from {
			height: 0;
		}
	}

	.voice {
		display: grid;
		place-items: center;
		flex: none;
		width: 2.6em;
		height: 2.6em;
		border-radius: 50%;
		background: $accent;

		.recording > & {
			background: #dd2d44;
		}

		svg {
			width: 1.3em;
			height: 1.3em;
			fill: #ffffff;
			stroke: #ffffff;
			stroke-width: 2;
			stroke-linecap: round;
		}

		path {
			fill: none;
		}
	}

	.board {
		grid-column: 1 / -1;
		width: 100%;
		height: auto;
		border-radius: 0.8em;
		box-shadow: rgba(75, 75, 75, 0.12) -0.25em 0.5em 1.15em 0.2em;
	}

	.bread {
		fill: #f4f1ea;
	}

	.rail {
		fill: none;
		stroke: #e06a5a;
		stroke-width: 1;
	}

	.holes {
		fill: none;
		stroke: #b9b4a8;
		stroke-width: 2.4;
		stroke-linecap: round;
		stroke-dasharray: 0.1 7.9;
	}

	.wire {
		fill: none;
		stroke: #e5484d;
		stroke-width: 2.5;
		stroke-linecap: round;

		&.blue {
			stroke: #3e7bd6;
		}

		&.yellow {
			stroke: #f0b429;
		}
	}

	.chip,
	.buzzer {
		fill: #1d1f24;
	}

	.shield {
		fill: #b8bcc6;
	}

	.port {
		fill: #8a8f9c;
	}

	.led {
		fill: #5c2a2a;

		.on & {
			fill: #ff4d4d;
		}
	}

	.pin {
		fill: none;
		stroke: #d4a72c;
		stroke-width: 2;
	}

	.buzzer-hole {
		fill: #4a4d57;
	}

	.motor {
		fill: #e8e8ec;
	}

	.prop {
		fill: #e5484d;
	}

	.message {
		min-width: 0;
		overflow-wrap: anywhere;
		width: fit-content;
		max-width: 92%;
		padding: 0.6em 1em;
		border-radius: 0.5em 0.5em 1em 1em;
		font-size: 0.95em;

		&.user {
			justify-self: end;
			background: $background-2;
		}

		&.reply {
			background: $accent;
			color: #ffffff;
		}

		&.call {
			display: flex;
			align-items: center;
			gap: 0.8em;
			padding: 0.4em 0.9em 0.4em 0.4em;
			border: 0.1em solid $green;
			border-radius: 0.5em;
			background: $background-1;

			span {
				display: grid;
				gap: 0.15em;
				font-size: 0.8em;
				font-weight: 500;
			}

			code {
				font-family: var(--mono);
				font-size: 1.05em;
			}

			i {
				position: relative;
				flex: none;
				width: 2.4em;
				height: 2.4em;
				border-radius: 0.5em;
				background: $green;

				// the white tick
				&::after {
					content: '';
					position: absolute;
					top: 26%;
					left: 36%;
					width: 26%;
					height: 42%;
					border: solid #ffffff;
					border-width: 0 0.24em 0.24em 0;
					rotate: 45deg;
				}
			}
		}
	}
</style>
