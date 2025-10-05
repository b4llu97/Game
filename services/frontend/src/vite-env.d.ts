/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_ORCHESTRATOR_URL: string
  readonly VITE_ASR_URL: string
  readonly VITE_TTS_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
