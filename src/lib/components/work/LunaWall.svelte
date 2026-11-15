<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { picture } from '#lib/content/site.ts';
	import { gsap, POINTER_MOTION, type Span } from '#lib/motion/gsap.ts';

	type Layer = 'infrastructure' | 'console' | 'servers' | 'game client';

	const LAYERS: Layer[] = ['infrastructure', 'console', 'servers', 'game client'];

	const TILES = {
		machines: { layer: 'infrastructure', picture: picture('luna/wall/machines.webp', 'the machines in the cluster') },
		health: { layer: 'infrastructure', picture: picture('luna/wall/machine-health.webp', 'health checks for one machine') },
		proxy: { layer: 'infrastructure', picture: picture('luna/wall/proxy.webp', 'proxy routing') },
		banner: { layer: 'console', picture: picture('luna/wall/console-banner.webp', 'luna Console banner') },
		terminal: { layer: 'console', picture: picture('luna/wall/terminal.webp', 'the console\'s terminal') },
		serial: { layer: 'console', picture: picture('luna/wall/instance-console.webp', 'a live server console') },
		instances: { layer: 'servers', picture: picture('luna/wall/instances.webp', 'every server on one screen') },
		monitoring: { layer: 'servers', picture: picture('luna/wall/monitoring.webp', 'server monitoring charts') },
		plugins: { layer: 'servers', picture: picture('luna/wall/plugins.webp', 'the plugin list') },
		world: { layer: 'servers', picture: picture('luna/wall/world.webp', 'world backups') },
		create: { layer: 'servers', picture: picture('luna/wall/create-banner.webp', 'luna Create banner') },
		racing: { layer: 'game client', picture: picture('luna/wall/boat-racing.webp', 'the boat racing event') },
		lantern: { layer: 'game client', picture: picture('luna/wall/lantern.webp', 'a lantern over the survival world') }
	} as const;

	const COLUMNS: (keyof typeof TILES)[][] = [
		['monitoring', 'lantern', 'machines', 'terminal', 'create', 'health'],
		['serial', 'proxy', 'racing', 'create', 'plugins', 'lantern'],
		['health', 'instances', 'banner', 'world', 'racing', 'terminal'],
		['plugins', 'racing', 'monitoring', 'lantern', 'instances', 'banner']
	];

	const POINTER_TILT = 4;

	let root = $state<HTMLDivElement>();

	/**
	 * Flies the camera across the wall and lights each layer in turn.
	 *
	 * @param timeline the work stack's scrubbed timeline
	 * @param at where this card's half-unit of scroll starts
	 * @param shown the stretch of the timeline over which this card is on screen
	 */
	export function animate(timeline: gsap.core.Timeline, at: number, shown: Span): void {
		const scope = gsap.utils.selector(root!);
		const step = 0.5 / LAYERS.length;

		timeline
			.fromTo(scope('.wall'), { yPercent: -2 }, { yPercent: -36, duration: shown.to - shown.from, ease: 'none' }, shown.from)
			.fromTo(scope('.column:nth-child(odd)'), { y: '-4rem' }, { y: '4rem', duration: shown.to - shown.from, ease: 'none' }, shown.from)
			.fromTo(scope('.column:nth-child(even)'), { y: '4rem' }, { y: '-4rem', duration: shown.to - shown.from, ease: 'none' }, shown.from);

		LAYERS.forEach((layer, index) => {
			const lit = scope(`[data-layer="${layer}"]`);
			const start = at + index * step;

			timeline.to(lit, { '--lit': 1, duration: step * 0.3, ease: 'power1.out' }, start);

			if (index < LAYERS.length - 1) {
				timeline.to(lit, { '--lit': 0, duration: step * 0.3, ease: 'power1.in' }, start + step * 0.8);
			}
		});
	}

	onMount(() => {
		const media = gsap.matchMedia();

		media.add(POINTER_MOTION, () => {
			const camera = root!.querySelector('.camera');
			const tiltX = gsap.quickTo(camera, 'rotationX', { duration: 1, ease: 'power3.out' });
			const tiltY = gsap.quickTo(camera, 'rotationY', { duration: 1, ease: 'power3.out' });

			const follow = (event: PointerEvent): void => {
				tiltY((event.clientX / window.innerWidth - 0.5) * POINTER_TILT);
				tiltX((0.5 - event.clientY / window.innerHeight) * POINTER_TILT);
			};

			window.addEventListener('pointermove', follow);

			return () => window.removeEventListener('pointermove', follow);
		});

		return () => media.revert();
	});
</script>

<div class="luna" bind:this={root}>
	<div class="camera">
		<div class="wall">
			{#each COLUMNS as column, order (order)}
				<div class="column">
					{#each column as name, index (index)}
						{@const tile = TILES[name]}
						<img
							src={tile.picture.src}
							width={tile.picture.width}
							height={tile.picture.height}
							alt={tile.picture.alt}
							data-layer={tile.layer}
							loading="lazy"
						/>
					{/each}
				</div>
			{/each}
		</div>
	</div>

	<ul class="layers">
		{#each LAYERS as layer (layer)}
			<li data-layer={layer}>{layer}</li>
		{/each}
	</ul>
</div>

<style lang="scss">
	.luna {
		position: relative;
		height: 100%;
		min-height: 20rem;
		border-radius: 1.5rem;
		background: var(--night);
		overflow: hidden;
		perspective: 70rem;
	}

	.camera {
		@include fill;
		transform-style: preserve-3d;
	}

	.wall {
		position: absolute;
		top: 0;
		left: -45%;
		display: flex;
		gap: 1.25rem;
		width: 190%;
		transform-style: preserve-3d;
		// the camera angle: looking across the wall from its near edge
		transform: rotateX(52deg) rotateZ(-14deg);
		transform-origin: 50% 30%;
	}

	.column {
		display: grid;
		flex: 1;
		align-content: start;
		gap: 1.25rem;

		img {
			--lit: 0;
			width: 100%;
			height: auto;
			border-radius: 0.75rem;
			transform: translateZ(calc(var(--lit) * 3rem));
			box-shadow: 0 0 0 calc(var(--lit) * 0.25rem) var(--lav);
		}
	}

	// the far edge of the wall fades into the dark
	.luna::after {
		content: '';
		position: absolute;
		inset: 0 0 45% 0;
		background: linear-gradient(var(--night), transparent);
		pointer-events: none;
	}

	.layers {
		@include label;
		position: absolute;
		left: 1rem;
		bottom: 1rem;
		z-index: 1;
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;

		li {
			--lit: 0;
			padding: 0.375rem 0.75rem;
			border-radius: 1rem;
			background: color-mix(in srgb, var(--lav) calc(var(--lit) * 100%), rgba(255, 255, 255, 0.14));
			color: color-mix(in srgb, var(--night) calc(var(--lit) * 100%), var(--paper));
		}
	}
</style>
