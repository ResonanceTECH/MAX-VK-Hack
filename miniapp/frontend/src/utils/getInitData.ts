/**
 * Утилита для получения initData из Max WebApp
 * Поддерживает различные способы передачи данных от Max
 */

export function getInitData(): string {
  // Способ 1: из window.MaxWebApp (основной способ)
  if (window.MaxWebApp?.initData) {
    return window.MaxWebApp.initData
  }
  
  // Способ 2: из URL параметров (query string)
  const urlParams = new URLSearchParams(window.location.search)
  let initData = urlParams.get('initData') || urlParams.get('tgWebAppData') || ''
  
  if (initData) {
    return initData
  }
  
  // Способ 3: из hash параметров
  if (window.location.hash) {
    const hashParams = new URLSearchParams(window.location.hash.substring(1))
    initData = hashParams.get('initData') || hashParams.get('tgWebAppData') || ''
  }
  
  return initData
}

