<!-- Copyright (c) 2026 Belikhun. All rights reserved.
     Proprietary software: use, copying, modification and distribution are
     prohibited without written permission. See LICENSE at the repository root. -->

<script lang="ts">
	import About from '#lib/components/About.svelte';
	import Band from '#lib/components/Band.svelte';
	import Contact from '#lib/components/Contact.svelte';
	import Hero from '#lib/components/Hero.svelte';
	import Loader from '#lib/components/Loader.svelte';
	import Nav from '#lib/components/Nav.svelte';
	import OffHours from '#lib/components/OffHours.svelte';
	import Rows from '#lib/components/Rows.svelte';
	import Timeline from '#lib/components/Timeline.svelte';
	import Work from '#lib/components/Work.svelte';
</script>

<svelte:head>
	<title>belikhun</title>
	<meta name="description" content="belikhun: fullstack web engineer from Việt Nam. frameworks, platforms and the servers they run on." />
</svelte:head>

<Loader />
<Nav />

<main>
	<Hero />
	<About />
	<Timeline />
	<Band />
	<Work />
	<Rows />
	<OffHours />
	<Contact />
</main>
