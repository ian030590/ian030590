import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://ian030590.trainerhub.cc',
  output: 'static',
  publicDir: './.generated/public',
  build: { format: 'file' },
});
