import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';

// pnpm dev     – dev server with instant reload, dev mode on
// pnpm build   – two self-contained single files (JS, CSS and the song inlined):
//   dist/dev/index.html      dev mode on at start
//   dist/release/index.html  dev mode off at start
// Dev mode can always be toggled in the game with the key left of «1».
export default defineConfig(({ command, mode }) => ({
  plugins: [viteSingleFile()],
  define: { __DEV_MODE_DEFAULT__: JSON.stringify(command === 'serve' || mode === 'devbuild') },
  build: {
    outDir: mode === 'devbuild' ? 'dist/dev' : 'dist/release',
    emptyOutDir: true,
    assetsInlineLimit: 50_000_000,
    target: 'es2022',
  },
}));
