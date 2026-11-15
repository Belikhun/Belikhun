<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import { onMount } from 'svelte';

	import { WORKS } from '#lib/content/site.ts';
	import { gsap, MOTION, ScrollTrigger } from '#lib/motion/gsap.ts';

	// A flock of cursors, one per project, that circles the visitor's pointer.
	// The idea comes from Joel Califa's Swarm (califa.github.io/swarm-site); the
	// cursors, the motion and the code are this site's own.

	interface Agent {
		element: HTMLElement;
		x: number;
		y: number;
		velocityX: number;
		velocityY: number;
		angle: number;
		orbit: number;
		speed: number;
	}

	const TONES = ['pink', 'blue', 'lav'];

	/** How hard an agent is pulled towards its place on the ring, per second squared. */
	const PULL = 14;

	/** Velocity kept per frame; lower settles faster. */
	const DRAG = 0.9;

	/** Agents closer than this push each other apart, in rem. */
	const PERSONAL_SPACE = 6;

	/** The nearest ring around the pointer and the step to each ring beyond it, in rem. */
	const ORBIT = 12;
	const ORBIT_STEP = 7;

	let root = $state<HTMLDivElement>();

	onMount(() => {
		const media = gsap.matchMedia();

		media.add(MOTION, () => {
			const host = root!;
			const rem = parseFloat(getComputedStyle(document.documentElement).fontSize);
			const space = PERSONAL_SPACE * rem;
			const target = { x: host.clientWidth / 2, y: host.clientHeight / 2 };
			const aim = { ...target };

			const agents: Agent[] = gsap.utils.toArray<HTMLElement>('.agent', host).map((element, index, all) => {
				gsap.set(element, { left: 0, top: 0 });

				return {
					element,
					x: Math.random() * host.clientWidth,
					y: host.clientHeight + 80,
					velocityX: 0,
					velocityY: 0,
					angle: (index / all.length) * Math.PI * 2,
					orbit: (ORBIT + (index % 3) * ORBIT_STEP) * rem,
					speed: 0.25 + (index % 4) * 0.06
				};
			});

			const follow = (event: PointerEvent): void => {
				const box = host.getBoundingClientRect();
				const inside = event.clientY > box.top && event.clientY < box.bottom;

				aim.x = inside ? event.clientX - box.left : box.width / 2;
				aim.y = inside ? event.clientY - box.top : box.height / 2;
			};

			const step = (_time: number, deltaMs: number): void => {
				const delta = Math.min(deltaMs, 50) / 1000;

				target.x += (aim.x - target.x) * 0.08;
				target.y += (aim.y - target.y) * 0.08;

				for (const agent of agents) {
					agent.angle += agent.speed * delta;

					let pullX = target.x + Math.cos(agent.angle) * agent.orbit - agent.x;
					let pullY = target.y + Math.sin(agent.angle) * agent.orbit * 0.6 - agent.y;

					for (const other of agents) {
						if (other === agent) {
							continue;
						}

						const apartX = agent.x - other.x;
						const apartY = agent.y - other.y;
						const distance = Math.hypot(apartX, apartY);

						if (distance > 0 && distance < space) {
							const push = (space - distance) / distance;

							pullX += apartX * push;
							pullY += apartY * push;
						}
					}

					agent.velocityX = (agent.velocityX + pullX * PULL * delta) * DRAG;
					agent.velocityY = (agent.velocityY + pullY * PULL * delta) * DRAG;
					agent.x += agent.velocityX * delta;
					agent.y += agent.velocityY * delta;
					agent.element.style.transform = `translate3d(${agent.x}px, ${agent.y}px, 0)`;
				}
			};

			const trigger = ScrollTrigger.create({
				trigger: host,
				start: 'top bottom',
				end: 'bottom top',
				onToggle: (self) => {
					if (self.isActive) {
						gsap.ticker.add(step);
					} else {
						gsap.ticker.remove(step);
					}
				}
			});

			window.addEventListener('pointermove', follow);

			return () => {
				window.removeEventListener('pointermove', follow);
				gsap.ticker.remove(step);
				trigger.kill();
			};
		});

		return () => media.revert();
	});
</script>

<div class="flock" bind:this={root} aria-hidden="true">
	{#each WORKS as work, index (work.name)}
		<div
			class="agent {TONES[index % TONES.length]}"
			style:left="{8 + ((index * 37) % 84)}%"
			style:top="{18 + ((index * 53) % 60)}%"
		>
			<svg viewBox="0 0 18 23"><path d="M2 2 2 18 6.8 13.6 10.4 21.4 13 20.2 9.5 12.6 16 12.6Z" /></svg>
			<span>{work.name}</span>
		</div>
	{/each}
</div>

<style lang="scss">
	.flock {
		@include fill;
		overflow: hidden;
		pointer-events: none;
	}

	.agent {
		position: absolute;
		display: flex;
		align-items: flex-start;
		will-change: transform;

		svg {
			width: 1.125rem;
			fill: var(--pink);
			stroke: var(--night);
			stroke-width: 1.2;
			stroke-linejoin: round;
		}

		span {
			margin: 0.875rem 0 0 0.125rem;
			padding: 0.125rem 0.5rem;
			border-radius: 0.75rem;
			background: var(--pink);
			color: var(--night);
			font-size: 0.75rem;
			font-weight: 500;
			white-space: nowrap;
		}

		&.blue {
			svg {
				fill: var(--blue);
			}

			span {
				background: var(--blue);
			}
		}

		&.lav {
			svg {
				fill: var(--paper);
			}

			span {
				background: var(--paper);
			}
		}
	}
</style>
