<script setup>
defineProps({ name: { type: String, default: "grid" } });
const paths = {
  grid: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
  vote: "m8 10 3 3 5-6 M5 16l-2 5h18l-2-5 M5 3h14v13H5z",
  user: "M20 21v-2a7 7 0 0 0-14 0v2 M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0",
  shield: "m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6z m-4 9 3 3 5-6",
  arrow: "M4 12h16 m-6-6 6 6-6 6",
  wallet: "M3 6h17v15H3z M3 6V3h14v3 M15 11h6v5h-6z",
  check: "m5 12 4 4L19 6",
  globe:
    "M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0 M3 12h18 M12 3c5 6 5 12 0 18-5-6-5-12 0-18",
  clock: "M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0 M12 7v5l3 2",
  camera: "M3 7h4l2-3h6l2 3h4v14H3z M16 13a4 4 0 1 1-8 0 4 4 0 0 1 8 0",
  refresh: "M20 7a9 9 0 1 0 1 9 M20 3v5h-5",
  chart: "M4 20V10 M12 20V4 M20 20v-7",
};
</script>
<template>
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.6"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path :d="paths[name] || paths.grid" />
  </svg>
</template>
