import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: './openapi.json',
  output: {
    path: 'src/generated',
    format: 'prettier',
    lint: 'eslint',
  },
  plugins: [
    '@hey-api/typescript',
    '@hey-api/sdk',
    {
      name: '@hey-api/client-fetch',
    },
    {
      name: '@tanstack/react-query',
    },
  ],
});
