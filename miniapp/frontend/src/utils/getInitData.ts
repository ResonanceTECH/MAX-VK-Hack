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

/**
 * Извлекает user_id из initData
 * @param initData - строка initData в формате query string
 * @returns user_id или null, если не удалось извлечь
 */
export function extractUserIdFromInitData(initData: string): number | null {
  try {
    const params = new URLSearchParams(initData)
    const userStr = params.get('user')
    
    if (!userStr) {
      return null
    }
    
    // Декодируем URL-encoded строку
    const decodedUserStr = decodeURIComponent(userStr)
    const userData = JSON.parse(decodedUserStr)
    
    return userData.id || null
  } catch (error) {
    console.error('Ошибка извлечения user_id из initData:', error)
    return null
  }
}

/**
 * Получает user_id текущего пользователя из Max WebApp
 * @returns user_id или null, если не удалось получить
 */
export function getCurrentUserId(): number | null {
  const initData = getInitData()
  if (!initData) {
    return null
  }
  
  return extractUserIdFromInitData(initData)
}

