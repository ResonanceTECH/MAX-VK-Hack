/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SCHEDULE_API_URL?: string
  readonly VITE_API_BASE_URL?: string
  // добавьте другие переменные окружения по мере необходимости
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

