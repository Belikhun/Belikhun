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
			}
		});

		return () => trigger.kill();
	});
</script>

<header class="nav" class:hidden>
	<a class="brand" href="#top">belikhun.dev</a>
	<nav class="links" aria-label="sections">
		{#each LINKS as link (link.href)}
			<a href={link.href}>{link.text}</a>
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
		transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);

		&.hidden {
			transform: translateY(-110%);
		}
	}

	.brand,
	.links {
		pointer-events: auto;
	}

	.brand {
		font-weight: 600;
	}

	.links {
		display: flex;
		align-items: center;
		gap: 1.25rem;
		padding: 0.5rem 1.25rem;
		border-radius: 2rem;
		background: color-mix(in srgb, var(--bg) 86%, transparent);
		backdrop-filter: blur(0.75rem);
		font-size: 0.875rem;

		a {
			transition: color 0.2s;

			&:hover {
				color: var(--purple);
			}

			@include below($bp-narrow) {
				display: none;
			}
		}
	}

	.theme {
		@include bare-button;
		@include label;
		padding: 0.25rem 0.75rem;
		border-radius: 1rem;
		background: var(--ink);
		color: var(--bg);
	}
</style>
