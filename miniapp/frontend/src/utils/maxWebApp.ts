// Типы для Max WebApp (аналогично Telegram WebApp)
// Max передает данные через window объект при открытии мини-приложения
declare global {
  interface Window {
    MaxWebApp?: {
      initData: string
      initDataUnsafe: {
        user?: {
          id: number
          first_name: string
          last_name?: string
          username?: string
        }
        auth_date: number
      }
      version: string
      platform: string
      ready: () => void
      expand: () => void
      close: () => void
      sendData: (data: string) => void
      onEvent: (eventType: string, eventHandler: () => void) => void
      offEvent: (eventType: string, eventHandler: () => void) => void
    }
    // Альтернативный способ получения initData через URL параметры
    location: Location & {
      search: string
    }
  }
}

export class MaxWebApp {
  static getInstance() {
    return window.MaxWebApp
  }

  static getInitData(): string {
    // Пытаемся получить из window.MaxWebApp
    if (window.MaxWebApp?.initData) {
      return window.MaxWebApp.initData
    }
    
    // Альтернативно: получаем из URL параметров (если Max передает так)
    const urlParams = new URLSearchParams(window.location.search)
    const initData = urlParams.get('initData') || urlParams.get('tgWebAppData') || ''
    
    return initData
  }

  static getUser() {
    return window.MaxWebApp?.initDataUnsafe?.user
  }

  static ready() {
    if (window.MaxWebApp?.ready) {
      window.MaxWebApp.ready()
    }
  }

  static expand() {
    if (window.MaxWebApp?.expand) {
      window.MaxWebApp.expand()
    }
  }
}

