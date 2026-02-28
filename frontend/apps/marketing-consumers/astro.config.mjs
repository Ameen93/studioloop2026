import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  site: process.env.SITE_URL || 'https://app.studioloop.co.za',
  publicDir: '../../public',
});
