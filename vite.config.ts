// Copyright (c) 2026 Belikhun. All rights reserved.
// Proprietary software: use, copying, modification and distribution are
// prohibited without written permission. See LICENSE at the repository root.

import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vite';
import { resolve } from 'node:path';

/** every `<style lang="scss">` block gets the shared partial for free */
const STYLE_ROOT = resolve(import.meta.dirname, 'src/lib/styles');

export default defineConfig({
	plugins: [
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter({ pages: 'build', assets: 'build' }),
			preprocess: vitePreprocess()
		})
	],

	css: {
		preprocessorOptions: {
			scss: {
				loadPaths: [STYLE_ROOT],
				additionalData: '@use \'shared\' as *;\n'
			}
		}
	}
});
