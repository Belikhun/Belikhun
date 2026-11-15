<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { CLIENTS, ROWS, type Row } from '#lib/content/site.ts';
	import { gsap, MOTION, POINTER_MOTION } from '#lib/motion/gsap.ts';

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
	<h2>everything else</h2>

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

	<div class="clients">
		<p>worked for</p>
		<ul>
			{#each CLIENTS as client (client)}
				<li>{client}</li>
			{/each}
		</ul>
	</div>

	<div class="preview" class:shown={hovered} aria-hidden="true">
		{#if hovered?.preview}
			<img src={hovered.preview.src} width={hovered.preview.width} height={hovered.preview.height} alt="" />
		{:else if hovered}
			<span>{hovered.name}</span>
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

	.row {
		--drawn: 1;
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) 4rem 1.5rem;
		align-items: baseline;
		gap: 1rem;
		padding: 1.25rem 1rem;
		overflow: hidden;
		transition: background-color 0.25s, padding-left 0.35s cubic-bezier(0.22, 1, 0.36, 1);

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

		&:hover {
			padding-left: 2rem;
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

		span {
			@include display;
			display: grid;
			place-items: center;
			height: 10rem;
			padding: 1rem;
			font-size: 1.75rem;
			line-height: 1;
			text-align: center;
		}
	}
</style>
