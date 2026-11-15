<!-- Copyright (c) 2026 Belikhun. Licensed under the MIT License.
     See LICENSE at the repository root. -->

<script lang="ts">
	import '@fontsource-variable/bricolage-grotesque';
	import '@fontsource-variable/lexend';
	import '@fontsource-variable/jetbrains-mono';
	import '../app.scss';

	import { onMount, type Snippet } from 'svelte';

	import { ScrollTrigger } from '#lib/motion/gsap.ts';
	import { startSmoothScroll } from '#lib/motion/stage.ts';

	let { children }: { children: Snippet } = $props();

	onMount(() => {
		const stop = startSmoothScroll();

		// the pinned scenes measure text; measure again once the real fonts are in
		document.fonts.ready.then(() => ScrollTrigger.refresh());

		return stop;
	});
</script>

{@render children()}
