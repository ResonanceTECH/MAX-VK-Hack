"""Обработчик модуля для администраторов"""
from typing import Dict, Any
import logging
from handlers.base import BaseHandler
from utils.keyboard import (
    create_admin_main_keyboard,
    create_dashboard_keyboard,
    create_analytics_keyboard,
    create_attendance_analytics_keyboard,
    create_inline_keyboard,
    create_callback_button
)
from utils.states import (
    get_user_role,
    set_user_role
)
from utils.storage import (
    UNIVERSITY_METRICS,
    FACULTY_ATTENDANCE,
    FACULTY_PERFORMANCE,
    REQUESTS_STATISTICS,
    FINANCIAL_METRICS
)

logger = logging.getLogger(__name__)


class AdminHandler(BaseHandler):
    """Обработчик модуля для администраторов"""
    
    def can_handle(self, update: Dict[str, Any]) -> bool:
        """Проверяет, относится ли обновление к модулю администраторов"""
        if update.get('update_type') == 'message_callback':
            payload = update.get('callback', {}).get('payload', '')
            # Обрабатываем payload'ы модуля администраторов
            return (payload.startswith(('admin_', 'analytics_')) 
                    or payload == 'admin_main')
        return False
    
    def handle(self, update: Dict[str, Any], api) -> None:
        """Обрабатывает обновление модуля администраторов"""
        callback = update.get('callback', {})
        payload = callback.get('payload', '')
        user = callback.get('user', {})
        user_id = user.get('user_id')
        user_name = user.get('first_name', 'Пользователь')
        message = update.get('message', {})
        recipient = message.get('recipient', {})
        chat_id = recipient.get('chat_id')
        
        logger.debug(f"AdminHandler обрабатывает payload: {payload}")
        
        role = get_user_role(user_id)
        
        # Главное меню администраторов - обрабатываем даже если роль не установлена
        if payload == 'admin_main' or payload == 'menu_admin':
            if role != 'admin':
                set_user_role(user_id, 'admin')
            self._show_admin_main(chat_id, user_name, api)
            return
        
        # Проверка роли для остальных действий
        if role != 'admin':
            api.send_message(
                chat_id=chat_id,
                text="⚠️ Этот раздел доступен только для администраторов.\nИспользуйте /role для смены роли."
            )
            return
        
        # Дашборд
        if payload == 'admin_dashboard':
            self._show_dashboard(chat_id, api)
        
        # Аналитика
        elif payload == 'admin_analytics':
            self._show_analytics_menu(chat_id, api)
        
        # Посещаемость по факультетам
        elif payload == 'analytics_attendance':
            self._show_attendance_analytics(chat_id, api)
        
        # График посещаемости
        elif payload == 'analytics_attendance_chart':
            self._show_attendance_chart(chat_id, api)
        
        # Сравнение посещаемости
        elif payload == 'analytics_attendance_comparison':
            self._show_attendance_comparison(chat_id, api)
        
        # Успеваемость
        elif payload == 'analytics_performance':
            self._show_performance_analytics(chat_id, api)
        
        # Заявки и обращения
        elif payload == 'analytics_requests':
            self._show_requests_analytics(chat_id, api)
        
        # Финансовые показатели
        elif payload == 'analytics_financial':
            self._show_financial_analytics(chat_id, api)
        
        # Экспорт данных
        elif payload == 'admin_export':
            self._show_export_options(chat_id, api)
        
        # Остальные разделы (в разработке)
        elif payload in ['admin_monitoring', 'admin_news']:
            api.send_message(
                chat_id=chat_id,
                text="🚧 Функционал в разработке",
                attachments=[self._create_back_button('admin_main')]
            )
        
        # Неизвестный payload
        else:
            logger.warning(f"Неизвестный payload в AdminHandler: {payload}")
            api.send_message(
                chat_id=chat_id,
                text="❌ Произошла ошибка. Попробуйте использовать /menu для возврата в меню."
            )
    
    def _show_admin_main(self, chat_id: int, user_name: str, api) -> None:
        """Показывает главное меню администраторов"""
        text = f"{user_name}, административный раздел:"
        keyboard = create_admin_main_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments)
    
    def _show_dashboard(self, chat_id: int, api) -> None:
        """Показывает дашборд с ключевыми показателями"""
        metrics = UNIVERSITY_METRICS
        students = metrics['students']
        
        change_sign = "+" if students['change_type'] == 'increase' else "-"
        
        text = (
            "**Ключевые показатели вуза:**\n\n"
            f"• **Студенты:** {students['total']:,} ({change_sign}{students['change']}%)\n"
            f"• **Посещаемость:** {metrics['attendance']}%\n"
            f"• **Успеваемость:** {metrics['performance']}/5.0\n"
            f"• **Заполненность кампуса:** {metrics['campus_occupancy']}%"
        )
        
        keyboard = create_dashboard_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_analytics_menu(self, chat_id: int, api) -> None:
        """Показывает меню выбора метрик для анализа"""
        text = "**Выберите метрику для анализа:**"
        keyboard = create_analytics_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_attendance_analytics(self, chat_id: int, api) -> None:
        """Показывает аналитику посещаемости по факультетам"""
        text = "**Посещаемость за апрель 2025:**\n\n"
        
        for key, faculty in FACULTY_ATTENDANCE.items():
            text += f"• {faculty['name']}: {faculty['attendance']}%\n"
        
        keyboard = create_attendance_analytics_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_attendance_chart(self, chat_id: int, api) -> None:
        """Показывает график посещаемости"""
        text = (
            "**График посещаемости:**\n\n"
            "🚧 Функционал отображения графика в разработке.\n"
            "В будущем здесь будет визуализация данных."
        )
        buttons = [
            [create_callback_button('🔙 Назад', 'analytics_attendance')],
            [create_callback_button('🏠 Главное меню', 'menu_main')]
        ]
        keyboard = create_inline_keyboard(buttons)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_attendance_comparison(self, chat_id: int, api) -> None:
        """Показывает сравнение посещаемости с прошлым месяцем"""
        text = "**Сравнение посещаемости с прошлым месяцем:**\n\n"
        
        for key, faculty in FACULTY_ATTENDANCE.items():
            current = faculty['attendance']
            previous = faculty['previous_month']
            change = current - previous
            change_sign = "+" if change >= 0 else ""
            change_emoji = "📈" if change >= 0 else "📉"
            
            text += (
                f"{change_emoji} **{faculty['name']}:**\n"
                f"  Текущий месяц: {current}%\n"
                f"  Прошлый месяц: {previous}%\n"
                f"  Изменение: {change_sign}{change}%\n\n"
            )
        
        buttons = [
            [create_callback_button('🔙 Назад', 'analytics_attendance')],
            [create_callback_button('🏠 Главное меню', 'menu_main')]
        ]
        keyboard = create_inline_keyboard(buttons)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_performance_analytics(self, chat_id: int, api) -> None:
        """Показывает аналитику успеваемости"""
        text = "**Успеваемость по факультетам:**\n\n"
        
        for key, faculty in FACULTY_PERFORMANCE.items():
            text += f"• {faculty['name']}: {faculty['average']}/5.0\n"
        
        buttons = [
            [create_callback_button('🔙 Назад', 'admin_analytics')],
            [create_callback_button('🏠 Главное меню', 'menu_main')]
        ]
        keyboard = create_inline_keyboard(buttons)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_requests_analytics(self, chat_id: int, api) -> None:
        """Показывает аналитику заявок и обращений"""
        stats = REQUESTS_STATISTICS
        
        text = (
            "**Заявки и обращения:**\n\n"
            f"• Всего заявок: {stats['total']}\n"
            f"• На рассмотрении: {stats['pending']}\n"
            f"• В обработке: {stats['in_progress']}\n"
            f"• Завершено: {stats['completed']}\n\n"
            "**По типам:**\n"
            f"• Справки: {stats['by_type']['certificates']}\n"
            f"• Командировки: {stats['by_type']['business_trips']}\n"
            f"• Академический отпуск: {stats['by_type']['academic_leave']}\n"
            f"• Прочие: {stats['by_type']['other']}"
        )
        
        buttons = [
            [create_callback_button('🔙 Назад', 'admin_analytics')],
            [create_callback_button('🏠 Главное меню', 'menu_main')]
        ]
        keyboard = create_inline_keyboard(buttons)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_financial_analytics(self, chat_id: int, api) -> None:
        """Показывает финансовые показатели"""
        finance = FINANCIAL_METRICS
        
        text = (
            "**Финансовые показатели:**\n\n"
            f"• **Бюджет:** {finance['budget']:,} руб\n"
            f"• **Расходы:** {finance['expenses']:,} руб\n"
            f"• **Доходы:** {finance['revenue']:,} руб\n"
            f"• **Остаток:** {finance['revenue'] - finance['expenses']:,} руб\n\n"
            "**По категориям расходов:**\n"
            f"• Образование: {finance['by_category']['education']:,} руб\n"
            f"• Исследования: {finance['by_category']['research']:,} руб\n"
            f"• Инфраструктура: {finance['by_category']['infrastructure']:,} руб"
        )
        
        buttons = [
            [create_callback_button('🔙 Назад', 'admin_analytics')],
            [create_callback_button('🏠 Главное меню', 'menu_main')]
        ]
        keyboard = create_inline_keyboard(buttons)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_export_options(self, chat_id: int, api) -> None:
        """Показывает опции экспорта данных"""
        text = (
            "**Экспорт данных:**\n\n"
            "🚧 Функционал экспорта в разработке.\n"
            "В будущем здесь будет возможность экспортировать данные в различных форматах."
        )
        buttons = [
            [create_callback_button('🔙 Назад', 'admin_dashboard')],
            [create_callback_button('🏠 Главное меню', 'menu_main')]
        ]
        keyboard = create_inline_keyboard(buttons)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _create_back_button(self, back_payload: str) -> Dict[str, Any]:
        """Создает кнопку назад"""
        buttons = [[create_callback_button('🔙 Назад', back_payload)]]
        return create_inline_keyboard(buttons)

