import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://ian.trainerhub.cc',
  output: 'static',
  publicDir: './.generated/public',
  build: { format: 'file' },
});
