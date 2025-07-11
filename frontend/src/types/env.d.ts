/**
 * Environment configuration for the frontend
 */

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_APP_TITLE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare global {
  interface Window {
    __VITE_API_BASE_URL__?: string;
  }
}

export {};
