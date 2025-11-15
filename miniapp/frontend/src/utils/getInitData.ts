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
 * Согласно документации Max: user.id (int64) - уникальный идентификатор пользователя MAX
 * @param initData - строка initData в формате query string (hash=xxx&user={"id":12345}&auth_date=xxx)
 * @returns user_id (max_user_id) или null, если не удалось извлечь
 */
export function extractUserIdFromInitData(initData: string): number | null {
  try {
    const params = new URLSearchParams(initData)
    const userStr = params.get('user')
    
    if (!userStr) {
      return null
    }
    
    // Декодируем URL-encoded строку (user передается как JSON в URL-encoded формате)
    const decodedUserStr = decodeURIComponent(userStr)
    const userData = JSON.parse(decodedUserStr)
    
    // Извлекаем user.id - это и есть max_user_id для верификации в БД
    return userData.id || null
  } catch (error) {
    console.error('Ошибка извлечения user_id из initData:', error)
    return null
  }
}

/**
 * Получает user_id текущего пользователя из Max WebApp
 * Пробует несколько способов для максимальной совместимости
 * @returns user_id или null, если не удалось получить
 */
export function getCurrentUserId(): number | null {
  // Способ 1: Прямой доступ через initDataUnsafe (самый надежный, если Max предоставляет)
  if (window.MaxWebApp?.initDataUnsafe?.user?.id) {
    const userId = window.MaxWebApp.initDataUnsafe.user.id
    console.log('[getCurrentUserId] Найден user_id через initDataUnsafe:', userId)
    return userId
  }
  
  // Способ 2: Извлечение из строки initData
  const initData = getInitData()
  if (initData) {
    const userId = extractUserIdFromInitData(initData)
    if (userId) {
      console.log('[getCurrentUserId] Найден user_id из initData строки:', userId)
      return userId
    }
    console.warn('[getCurrentUserId] initData есть, но не удалось извлечь user_id. initData:', initData.substring(0, 100))
  } else {
    console.warn('[getCurrentUserId] initData не найден. window.MaxWebApp:', {
      exists: !!window.MaxWebApp,
      hasInitData: !!window.MaxWebApp?.initData,
      hasInitDataUnsafe: !!window.MaxWebApp?.initDataUnsafe,
      hasUser: !!window.MaxWebApp?.initDataUnsafe?.user
    })
  }
  
  return null
}

