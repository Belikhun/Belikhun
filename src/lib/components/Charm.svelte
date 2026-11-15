<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	/**
	 * A teru teru bōzu charm hanging on a string, like the ones on the avatar's
	 * dress. The parts carry classes so a scene can cut the string or drop the doll.
	 */
	let {
		string = 120
	}: {
		/** Length of the string, in the drawing's own units */
		string?: number;
	} = $props();
</script>

<svg class="charm" viewBox="0 0 60 {string + 72}" aria-hidden="true">
	<line class="string" x1="30" y1="0" x2="30" y2={string + 4} />
	<g class="doll" transform="translate(0 {string})">
		<path class="body" d="M13 33 Q30 25 47 33 L55 67 Q42 60 30 67 Q18 60 5 67 Z" />
		<circle class="head" cx="30" cy="20" r="18" />
		<circle class="eye" cx="23.5" cy="19" r="1.8" />
		<circle class="eye" cx="36.5" cy="19" r="1.8" />
		<path class="smile" d="M26 25.5 Q30 28.5 34 25.5" />
	</g>
</svg>

<style lang="scss">
	.charm {
		display: block;
		width: 100%;
		overflow: visible;
	}

	.string {
		stroke: var(--ink);
		stroke-width: 1;
	}

	.body,
	.head {
		fill: var(--paper);
		stroke: var(--night);
		stroke-width: 1.6;
		stroke-linejoin: round;
	}

	.eye {
		fill: var(--night);
	}

	.smile {
		fill: none;
		stroke: var(--night);
		stroke-width: 1.4;
		stroke-linecap: round;
	}
</style>
