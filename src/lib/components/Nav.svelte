<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { ScrollTrigger } from '#lib/motion/gsap.ts';

	const THEME_KEY = 'belikhun:theme';
	const HIDE_AFTER = 200;

	const LINKS = [
		{ href: '#about', text: 'about' },
		{ href: '#timeline', text: 'timeline' },
		{ href: '#work', text: 'work' },
		{ href: '#off-hours', text: 'off-hours' },
		{ href: '#hi', text: 'hi' }
	];

	let hidden = $state(false);
	let night = $state(false);
	let current = $state('');
	let links = $state<HTMLElement>();
	let marker = $state({ left: 0, width: 0 });

	/** Finds the section that covers the middle of the window. */
	function locate(): void {
		const middle = window.innerHeight / 2;
		let found = '';

		for (const link of LINKS) {
			const section = document.querySelector(link.href);

			if (section && section.getBoundingClientRect().top <= middle) {
				found = link.href;
			}
		}

		current = found;
	}

	$effect(() => {
		const link = links?.querySelector<HTMLElement>(`[href="${current}"]`);

		if (link) {
			marker = { left: link.offsetLeft, width: link.offsetWidth };
		}
	});

	function toggleTheme(): void {
		night = !night;

		const theme = night
			? 'dark'
			: 'light';

		document.documentElement.dataset.theme = theme;

		try {
			localStorage.setItem(THEME_KEY, theme);
		} catch {
			// the choice still holds for this visit
		}
	}

	onMount(() => {
		const chosen = document.documentElement.dataset.theme;

		night = chosen
			? chosen === 'dark'
			: window.matchMedia('(prefers-color-scheme: dark)').matches;

		const trigger = ScrollTrigger.create({
			start: 0,
			end: 'max',
			onUpdate: (self) => {
				hidden = self.direction === 1 && self.scroll() > HIDE_AFTER;
				locate();
			}
		});

		return () => trigger.kill();
	});
</script>

<header class="nav" class:hidden>
	<a class="brand" href="#top">belikhun.dev</a>
	<nav class="links" aria-label="sections" bind:this={links}>
		<i class="marker" class:shown={current} style:--left="{marker.left}px" style:--width="{marker.width}px"></i>
		{#each LINKS as link (link.href)}
			<a href={link.href} class:current={link.href === current} aria-current={link.href === current ? 'true' : undefined}>{link.text}</a>
		{/each}
		<button class="theme" type="button" onclick={toggleTheme} aria-pressed={night}>
			{night ? 'day' : 'night'}
		</button>
	</nav>
</header>

<style lang="scss">
	.nav {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 50;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 1.5rem clamp(1.5rem, 4vw, 3rem);
		pointer-events: none;
		transition: transform 0.5s var(--ease-out);

		&.hidden {
			transform: translateY(-110%);
		}
	}

	.brand,
	.links {
		pointer-events: auto;
	}

	.brand,
	.links {
		border-radius: 2rem;
		background: color-mix(in srgb, var(--bg) 86%, transparent);
		backdrop-filter: blur(0.75rem);
		box-shadow: 0 0 0 var(--hairline) var(--line);
	}

	.brand {
		padding: 0.625rem 1.25rem;
		font-size: 0.875rem;
		font-weight: 600;
	}

	.links {
		position: relative;
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.375rem;
		font-size: 0.875rem;

		a {
			position: relative;
			padding: 0.25rem 0.75rem;
			border-radius: 2rem;
			transition: color var(--fast) var(--ease-snap);

			&:hover {
				color: var(--accent-text);
			}

			&.current {
				color: var(--night);
			}

			@include below($bp-narrow) {
				display: none;
			}
		}
	}

	// slides under whichever section is on screen
	.marker {
		position: absolute;
		top: 0.375rem;
		bottom: 0.375rem;
		left: 0;
		width: var(--width);
		border-radius: 2rem;
		background: var(--pink);
		opacity: 0;
		translate: var(--left) 0;
		transition: translate 0.6s var(--ease-out), width 0.6s var(--ease-out), opacity 0.3s;

		&.shown {
			opacity: 1;
		}

		@include below($bp-narrow) {
			display: none;
		}
	}

	.theme {
		@include bare-button;
		@include label;
		position: relative;
		margin-left: 0.5rem;
		padding: 0.25rem 0.75rem;
		border-radius: 1rem;
		background: var(--ink);
		color: var(--bg);
	}
</style>
