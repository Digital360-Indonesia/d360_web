// @ts-check
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://digital360.id',
  output: 'static',
  integrations: [
    tailwind(),
    sitemap()
  ],
  image: {
    service: {
      entrypoint: 'astro/assets/services/sharp',
      config: {}
    },
  },
});
