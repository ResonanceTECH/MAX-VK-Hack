"""Обработчик модуля для сотрудников"""
from typing import Dict, Any
import logging
from handlers.base import BaseHandler
from utils.keyboard import (
    create_staff_main_keyboard,
    create_business_trips_keyboard,
    create_trip_dates_keyboard,
    create_trip_created_keyboard,
    create_my_trips_keyboard,
    create_inline_keyboard,
    create_callback_button
)
from utils.states import (
    get_user_role,
    set_user_role,
    get_user_state,
    set_user_state,
    clear_user_state,
    set_user_data,
    get_user_data,
    clear_user_data
)
from utils.storage import (
    create_business_trip,
    get_business_trips
)

logger = logging.getLogger(__name__)


class StaffHandler(BaseHandler):
    """Обработчик модуля для сотрудников"""
    
    def can_handle(self, update: Dict[str, Any]) -> bool:
        """Проверяет, относится ли обновление к модулю сотрудников"""
        if update.get('update_type') == 'message_callback':
            payload = update.get('callback', {}).get('payload', '')
            # Обрабатываем payload'ы модуля сотрудников
            return (payload.startswith(('staff_', 'trip_')) 
                    or payload == 'staff_main')
        return False
    
    def handle(self, update: Dict[str, Any], api) -> None:
        """Обрабатывает обновление модуля сотрудников"""
        callback = update.get('callback', {})
        payload = callback.get('payload', '')
        user = callback.get('user', {})
        user_id = user.get('user_id')
        user_name = user.get('first_name', 'Пользователь')
        message = update.get('message', {})
        recipient = message.get('recipient', {})
        chat_id = recipient.get('chat_id')
        
        logger.debug(f"StaffHandler обрабатывает payload: {payload}")
        
        role = get_user_role(user_id)
        
        # Главное меню сотрудников - обрабатываем даже если роль не установлена
        if payload == 'staff_main' or payload == 'menu_staff':
            if role != 'staff':
                set_user_role(user_id, 'staff')
            self._show_staff_main(chat_id, user_name, api)
            return
        
        # Проверка роли для остальных действий
        if role != 'staff':
            api.send_message(
                chat_id=chat_id,
                text="⚠️ Этот раздел доступен только для сотрудников.\nИспользуйте /role для смены роли."
            )
            return
        
        # Командировки
        if payload == 'staff_business_trips':
            self._show_business_trips(chat_id, api)
        
        # Подать заявку на командировку
        elif payload == 'trip_create':
            self._start_trip_application(chat_id, user_id, api)
        
        # Отмена заявки
        elif payload == 'trip_cancel':
            clear_user_data(user_id)
            clear_user_state(user_id)
            self._show_business_trips(chat_id, api)
            return
        
        # Выбор дат командировки
        elif payload.startswith('trip_date_'):
            self._handle_trip_date_selection(chat_id, user_id, payload, api)
        
        # Мои командировки
        elif payload == 'trip_my_trips':
            self._show_my_trips(chat_id, user_id, api)
        
        # Отчет по командировке
        elif payload == 'trip_report':
            self._show_trip_report(chat_id, api)
        
        # Остальные разделы (в разработке)
        elif payload in ['staff_vacation', 'staff_requests', 'staff_schedule']:
            api.send_message(
                chat_id=chat_id,
                text="🚧 Функционал в разработке",
                attachments=[self._create_back_button('staff_main')]
            )
        
        # Неизвестный payload
        else:
            logger.warning(f"Неизвестный payload в StaffHandler: {payload}")
            api.send_message(
                chat_id=chat_id,
                text="❌ Произошла ошибка. Попробуйте использовать /menu для возврата в меню."
            )
    
    def _show_staff_main(self, chat_id: int, user_name: str, api) -> None:
        """Показывает главное меню сотрудников"""
        text = f"{user_name}, раздел для сотрудников:"
        keyboard = create_staff_main_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments)
    
    def _show_business_trips(self, chat_id: int, api) -> None:
        """Показывает меню управления командировками"""
        text = "**Управление командировками:**"
        keyboard = create_business_trips_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _start_trip_application(self, chat_id: int, user_id: int, api) -> None:
        """Начинает процесс подачи заявки на командировку"""
        # Очищаем предыдущие данные
        clear_user_data(user_id, 'trip_purpose')
        clear_user_data(user_id, 'trip_city')
        clear_user_data(user_id, 'trip_date_from')
        clear_user_data(user_id, 'trip_date_to')
        
        # Устанавливаем состояние для ввода цели поездки
        set_user_state(user_id, 'trip_purpose')
        
        text = (
            "**Заполните заявку на командировку:**\n\n"
            "1. Цель поездки: [введите текст]"
        )
        api.send_message(chat_id=chat_id, text=text, attachments=[], format_type='markdown')
    
    def _handle_trip_date_selection(self, chat_id: int, user_id: int, payload: str, api) -> None:
        """Обрабатывает выбор дат командировки"""
        if payload == 'trip_date_15-18':
            # Предустановленные даты
            date_from = '15.04.2025'
            date_to = '18.04.2025'
            self._complete_trip_application(chat_id, user_id, date_from, date_to, api)
        elif payload == 'trip_date_custom':
            # Пользователь хочет ввести свои даты
            set_user_state(user_id, 'trip_date_custom')
            text = (
                "Введите даты в формате: ДД.ММ.ГГГГ - ДД.ММ.ГГГГ\n"
                "Например: 20.04.2025 - 25.04.2025"
            )
            api.send_message(chat_id=chat_id, text=text, attachments=[])
        else:
            api.send_message(chat_id=chat_id, text="❌ Ошибка выбора дат")
    
    def _complete_trip_application(self, chat_id: int, user_id: int, date_from: str, date_to: str, api) -> None:
        """Завершает создание заявки на командировку"""
        purpose = get_user_data(user_id, 'trip_purpose')
        city = get_user_data(user_id, 'trip_city')
        
        if not purpose or not city:
            api.send_message(chat_id=chat_id, text="❌ Ошибка: не все данные заполнены")
            return
        
        # Создаем командировку
        trip = create_business_trip(user_id, purpose, city, date_from, date_to)
        
        # Очищаем данные и состояние
        clear_user_data(user_id)
        clear_user_state(user_id)
        
        text = (
            f"✅ **Заявка на командировку #{trip['id']} создана!**\n\n"
            f"**Статус:** \"{trip['status']}\""
        )
        
        keyboard = create_trip_created_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_my_trips(self, chat_id: int, user_id: int, api) -> None:
        """Показывает командировки пользователя"""
        trips = get_business_trips(user_id)
        
        if not trips:
            text = "У вас пока нет командировок."
        else:
            text = "**Ваши командировки:**\n\n"
            for trip in trips:
                status_emoji = "✅" if trip['status'] == 'одобрено' else "⏳" if trip['status'] == 'На согласовании' else "📋"
                text += (
                    f"{status_emoji} #{trip['id']}\n"
                    f"Цель: {trip['purpose']}\n"
                    f"Город: {trip['city']}\n"
                    f"Даты: {trip['date_from']} - {trip['date_to']}\n"
                    f"Статус: {trip['status']}\n\n"
                )
        
        keyboard = create_my_trips_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_trip_report(self, chat_id: int, api) -> None:
        """Показывает форму отчета по командировке"""
        text = (
            "**Отчет по командировке:**\n\n"
            "🚧 Функционал в разработке"
        )
        buttons = [
            [create_callback_button('🔙 Назад', 'staff_business_trips')],
            [create_callback_button('🏠 Главное меню', 'menu_main')]
        ]
        keyboard = create_inline_keyboard(buttons)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _create_back_button(self, back_payload: str) -> Dict[str, Any]:
        """Создает кнопку назад"""
        buttons = [[create_callback_button('🔙 Назад', back_payload)]]
        return create_inline_keyboard(buttons)
    
    def handle_text_input(self, chat_id: int, user_id: int, text: str, api) -> bool:
        """Обрабатывает текстовый ввод для заполнения заявки на командировку"""
        state = get_user_state(user_id)
        
        if state == 'trip_purpose':
            # Сохраняем цель поездки
            set_user_data(user_id, 'trip_purpose', text)
            set_user_state(user_id, 'trip_city')
            
            api.send_message(
                chat_id=chat_id,
                text="2. Город назначения: [введите город]"
            )
            return True
        
        elif state == 'trip_city':
            # Сохраняем город
            set_user_data(user_id, 'trip_city', text)
            
            # Показываем выбор дат
            text_msg = "3. Даты поездки: [выберите период]"
            keyboard = create_trip_dates_keyboard()
            attachments = [keyboard]
            api.send_message(chat_id=chat_id, text=text_msg, attachments=attachments)
            return True
        
        elif state == 'trip_date_custom':
            # Парсим даты из текста
            try:
                dates = text.split(' - ')
                if len(dates) == 2:
                    date_from = dates[0].strip()
                    date_to = dates[1].strip()
                    # Простая валидация формата (можно улучшить)
                    if len(date_from) == 10 and len(date_to) == 10:
                        self._complete_trip_application(chat_id, user_id, date_from, date_to, api)
                        return True
            except:
                pass
            
            api.send_message(
                chat_id=chat_id,
                text="❌ Неверный формат дат. Используйте формат: ДД.ММ.ГГГГ - ДД.ММ.ГГГГ"
            )
            return True
        
        return False

