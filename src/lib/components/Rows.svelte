<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { CLIENT_WORK, CLIENTS, ROWS, type Row } from '#lib/content/site.ts';
	import { gsap, MOTION, POINTER_MOTION } from '#lib/motion/gsap.ts';
	import { reveal } from '#lib/motion/reveal.ts';

	import Emoji from './Emoji.svelte';

	let root = $state<HTMLElement>();
	let hovered = $state<Row>();

	function hover(event: PointerEvent): void {
		const row = (event.target as HTMLElement).closest<HTMLElement>('[data-row]');

		hovered = row
			? ROWS[Number(row.dataset.row)]
			: undefined;
	}

	onMount(() => {
		const context = gsap.context(() => {
			const media = gsap.matchMedia();

			media.add(MOTION, () => {
				gsap.from('.client', {
					y: '2rem',
					autoAlpha: 0,
					duration: 0.7,
					ease: 'power3.out',
					scrollTrigger: { trigger: '.client', start: 'top 85%' }
				});

				gsap.from('.row', {
					'--drawn': 0,
					duration: 0.9,
					stagger: 0.06,
					ease: 'power3.out',
					scrollTrigger: { trigger: '.list', start: 'top 80%' }
				});

				gsap.from('.row > *', {
					yPercent: 80,
					autoAlpha: 0,
					duration: 0.6,
					stagger: 0.02,
					ease: 'power3.out',
					scrollTrigger: { trigger: '.list', start: 'top 80%' }
				});
			});

			media.add(POINTER_MOTION, () => {
				const preview = root!.querySelector('.preview');
				const moveX = gsap.quickTo(preview, 'x', { duration: 0.5, ease: 'power3.out' });
				const moveY = gsap.quickTo(preview, 'y', { duration: 0.5, ease: 'power3.out' });
				const tilt = gsap.quickTo(preview, 'rotation', { duration: 0.6, ease: 'power3.out' });

				const follow = (event: PointerEvent): void => {
					moveX(event.clientX);
					moveY(event.clientY);
					tilt(gsap.utils.clamp(-12, 12, event.movementX * 0.6));
				};

				window.addEventListener('pointermove', follow);

				return () => window.removeEventListener('pointermove', follow);
			});
		}, root);

		return () => context.revert();
	});
</script>

<section class="rest" bind:this={root}>
	<h2 use:reveal>everything <span class="keep">else&nbsp;<Emoji code="1f4e6" char="📦" /></span></h2>

	<article class="client">
		<p class="meta">{CLIENT_WORK.context}</p>
		<h3>{CLIENT_WORK.name}</h3>
		<p class="body">{CLIENT_WORK.body}</p>
		<p class="role">{CLIENT_WORK.role}</p>
	</article>

	<ul class="list" onpointerover={hover} onpointerleave={() => (hovered = undefined)}>
		{#each ROWS as row, index (row.name)}
			<li>
				<svelte:element
					this={row.link ? 'a' : 'div'}
					class="row"
					href={row.link}
					target={row.link ? '_blank' : undefined}
					rel={row.link ? 'noreferrer' : undefined}
					data-row={index}
				>
					<span class="name">{row.name}</span>
					<span class="what">{row.what}</span>
					<span class="year">{row.year}</span>
					<span class="arrow" aria-hidden="true">{row.link ? '↗' : ''}</span>
				</svelte:element>
			</li>
		{/each}
	</ul>

	<div class="clients" use:reveal>
		<p>worked for</p>
		<ul>
			{#each CLIENTS as client (client)}
				<li>{client}</li>
			{/each}
		</ul>
	</div>

	<div class="preview" class:shown={hovered?.preview} aria-hidden="true">
		{#if hovered?.preview}
			<img src={hovered.preview.src} width={hovered.preview.width} height={hovered.preview.height} alt="" />
		{/if}
	</div>
</section>

<style lang="scss">
	.rest {
		@include gutter;
		display: grid;
		gap: 3rem;
		max-width: 90rem;
		margin-inline: auto;
		padding-block: 8rem;
	}

	h2 {
		@include display;
		font-size: clamp(2.5rem, 6vw, 6rem);
	}

	.keep {
		white-space: nowrap;
	}

	.client {
		display: grid;
		// the same columns as the rows below, so the two read as one table
		grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) 4rem 1.5rem;
		align-items: center;
		gap: 0.5rem 1rem;
		padding: 1.5rem 1rem;
		border: var(--hairline) solid var(--line);
		border-radius: 1.5rem;
		background: var(--surface);

		.meta {
			@include label;
			grid-column: 1 / -1;
			color: var(--soft);
		}

		h3 {
			@include display;
			font-size: clamp(2rem, 4vw, 3.5rem);
		}

		.body {
			grid-column: 2 / -1;
		}

		.role {
			@include label;
			grid-column: 2 / -1;
			color: var(--accent-text);
		}

		@include below($bp-medium) {
			grid-template-columns: minmax(0, 1fr);
			padding: 1.5rem;

			.body,
			.role {
				grid-column: 1 / -1;
			}
		}
	}

	.row {
		--drawn: 1;
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) 4rem 1.5rem;
		align-items: baseline;
		gap: 1rem;
		padding: 1.25rem 1rem;
		overflow: hidden;
		transition: background-color var(--fast) var(--ease-snap), padding-left 0.5s var(--ease-out), opacity var(--fast) var(--ease-snap);

		&::after {
			content: '';
			position: absolute;
			left: 0;
			right: 0;
			bottom: 0;
			height: var(--hairline);
			background: var(--line);
			transform: scaleX(var(--drawn));
			transform-origin: 0 50%;
		}

		// the row under the pointer stands out because the others step back
		@media (pointer: fine) {
			.list:has(a:hover) &:not(:hover) {
				opacity: 0.4;
			}
		}

		&:not(a):hover {
			background: color-mix(in srgb, var(--ink) 5%, transparent);
		}

		&:is(a):hover {
			padding-left: 2rem;
			border-radius: 0.75rem;
			background: var(--blue);
			color: var(--night);

			.what,
			.year {
				color: var(--night);
			}
		}

		@include below($bp-narrow) {
			grid-template-columns: minmax(0, 1fr) 3rem 1.5rem;

			.what {
				display: none;
			}
		}
	}

	.name {
		font-size: clamp(1.25rem, 2vw, 1.75rem);
		font-weight: 500;
	}

	.what,
	.year {
		@include label;
		color: var(--soft);
	}

	.clients {
		display: grid;
		gap: 1rem;

		p {
			@include label;
			color: var(--soft);
		}

		ul {
			display: flex;
			flex-wrap: wrap;
			gap: 0.5rem 0.75rem;
		}

		li {
			padding: 0.5rem 1.25rem;
			border: var(--hairline) solid var(--line);
			border-radius: 2rem;
			transition: background-color var(--fast) var(--ease-snap), border-color var(--fast) var(--ease-snap), translate var(--fast) var(--ease-snap);

			&:hover {
				border-color: var(--lav);
				background: var(--lav);
				color: var(--night);
				translate: 0 -0.125rem;
			}
		}
	}

	.preview {
		position: fixed;
		top: 0;
		left: 0;
		z-index: 20;
		display: none;
		width: 16rem;
		margin: -5rem 0 0 2rem;
		border-radius: 1rem;
		background: var(--lav);
		color: var(--night);
		overflow: hidden;
		pointer-events: none;
		opacity: 0;
		scale: 0.8;
		transition: opacity 0.2s, scale 0.3s cubic-bezier(0.22, 1, 0.36, 1);
		box-shadow: 0 1rem 2.5rem rgba(42, 36, 64, 0.24);

		@media (pointer: fine) {
			display: block;
		}

		&.shown {
			opacity: 1;
			scale: 1;
		}

		img {
			width: 100%;
			height: 10rem;
			object-fit: cover;
		}
	}
</style>
