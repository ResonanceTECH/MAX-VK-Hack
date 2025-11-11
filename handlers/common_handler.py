"""Общие обработчики для всех ролей"""
from typing import Dict, Any
from db.models import User
from utils.keyboard import create_main_menu_keyboard, create_role_selection_keyboard, create_help_menu_keyboard, create_admin_help_menu_keyboard
from utils.states import set_user_role, get_user_role
import logging

logger = logging.getLogger(__name__)


class CommonHandler:
    """Общие обработчики (меню, роли, помощь)"""
    
    def handle_start_after_greeting(self, user: Dict, max_user_id: int, api):
        """Обработать нажатие кнопки 'Начать' после приветствия"""
        # Получаем все роли пользователя
        all_roles = User.get_all_roles(max_user_id)
        
        if not all_roles:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет назначенных ролей. Обратитесь к администрации."
            )
            return
        
        # Если одна роль - показываем главное меню с этой ролью
        if len(all_roles) == 1:
            role_data = all_roles[0]
            role = role_data.get('role')
            # Сохраняем роль
            set_user_role(max_user_id, role)
            # Получаем пользователя с этой ролью
            user_data = User.get_by_max_id(max_user_id, role)
            if user_data:
                self.show_main_menu(user_data, max_user_id, api)
        else:
            # Если несколько ролей - показываем выбор роли
            self.show_role_selection(max_user_id, api)
    
    def show_main_menu(self, user: Dict, max_user_id: int, api):
        """Показать главное меню"""
        all_roles = User.get_all_roles(max_user_id)
        has_multiple_roles = len(all_roles) > 1
        
        greeting = {
            'student': f"👋 Привет, {user['fio']}!\n\nВыберите действие:",
            'teacher': f"👋 Здравствуйте, {user['fio']}!\n\nВыберите действие:",
            'admin': f"👋 Администратор {user['fio']}\n\nВыберите действие:",
            'support': f"👋 Поддержка {user['fio']}\n\nВыберите действие:"
        }
        
        keyboard = create_main_menu_keyboard(user['role'], has_multiple_roles)
        api.send_message(
            user_id=max_user_id,
            text=greeting.get(user['role'], 'Выберите действие:'),
            attachments=[keyboard]
        )
    
    def show_role_selection(self, max_user_id: int, api):
        """Показать выбор роли"""
        all_roles = User.get_all_roles(max_user_id)
        
        if not all_roles:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет назначенных ролей. Обратитесь к администрации."
            )
            return
        
        keyboard = create_role_selection_keyboard(all_roles)
        api.send_message(
            user_id=max_user_id,
            text="🔄 Выберите роль:",
            attachments=[keyboard]
        )
    
    def switch_role(self, max_user_id: int, role: str, api):
        """Переключиться на другую роль"""
        user = User.get_by_max_id(max_user_id, role)
        if not user:
            api.send_message(
                user_id=max_user_id,
                text="❌ Роль не найдена",
                attachments=[create_main_menu_keyboard('student')]
            )
            return
        
        # Сохраняем выбранную роль
        set_user_role(max_user_id, role)
        
        # Показываем главное меню с новой ролью
        all_roles = User.get_all_roles(max_user_id)
        has_multiple_roles = len(all_roles) > 1
        
        greeting = {
            'student': f"👋 Привет, {user['fio']}!\n\nВыберите действие:",
            'teacher': f"👋 Здравствуйте, {user['fio']}!\n\nВыберите действие:",
            'admin': f"👋 Администратор {user['fio']}\n\nВыберите действие:",
            'support': f"👋 Поддержка {user['fio']}\n\nВыберите действие:"
        }
        
        keyboard = create_main_menu_keyboard(role, has_multiple_roles)
        api.send_message(
            user_id=max_user_id,
            text=f"✅ Роль изменена на: {role}\n\n{greeting.get(role, 'Выберите действие:')}",
            attachments=[keyboard]
        )
    
    def show_help(self, role: str, max_user_id: int, api):
        """Показать справку"""
        if role == 'student':
            from utils.keyboard import create_help_menu_keyboard
            keyboard = create_help_menu_keyboard('student')
        elif role == 'teacher':
            from utils.keyboard import create_help_menu_keyboard
            keyboard = create_help_menu_keyboard('teacher')
        elif role in ['admin', 'support']:
            keyboard = create_admin_help_menu_keyboard(role)
        else:
            from utils.keyboard import create_help_menu_keyboard
            keyboard = create_help_menu_keyboard('student')
        
        api.send_message(
            user_id=max_user_id,
            text="❓ Помощь\n\nВыберите раздел:",
            attachments=[keyboard]
        )
    
    def show_help_faq(self, user: Dict, max_user_id: int, api):
        """Показать FAQ"""
        from utils.keyboard import create_back_keyboard
        text = "❓ Часто задаваемые вопросы (FAQ):\n\n"
        text += "1. Как написать преподавателю?\n"
        text += "   → Выберите 'Преподаватели' → 'Написать преподавателю'\n\n"
        text += "2. Как посмотреть список группы?\n"
        text += "   → Выберите 'Моя группа' → 'Список студентов'\n\n"
        text += "3. Как написать сокурснику?\n"
        text += "   → Выберите 'Моя группа' → 'Написать сокурснику'\n\n"
        text += "4. Как посмотреть расписание?\n"
        text += "   → Выберите 'Расписание' → 'На сегодня' или 'На неделю'\n\n"
        text += "5. Как получить помощь?\n"
        text += "   → Выберите 'Помощь' → 'Связь с поддержкой'"
        
        keyboard = create_back_keyboard("help")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_help_support(self, user: Dict, max_user_id: int, api):
        """Показать связь с поддержкой"""
        from db.connection import execute_query
        from utils.keyboard import create_back_keyboard
        support_query = """
            SELECT id, max_user_id, first_name, last_name, middle_name, role, phone, email,
                   TRIM(CONCAT_WS(' ', last_name, first_name, middle_name)) as fio
            FROM users
            WHERE role = 'support'
            LIMIT 1
        """
        support_user = execute_query(support_query, (), fetch_one=True)
        
        if not support_user:
            text = "💬 Связь с поддержкой:\n\n"
            text += "⚠️ Поддержка временно недоступна. Обратитесь к администратору."
            keyboard = create_back_keyboard("help")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
            return
        
        text = "💬 Связь с поддержкой:\n\n"
        text += "Если у вас возникли вопросы или проблемы, вы можете написать в поддержку.\n"
        text += "Ваше обращение будет зарегистрировано как тикет, и с вами свяжутся в ближайшее время."
        
        buttons = [[
            {"type": "callback", "text": "✉️ Написать в поддержку", "payload": f"write_support_{support_user['id']}"}
        ]]
        buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "help"}])
        keyboard = {
            "type": "inline_keyboard",
            "payload": {"buttons": buttons}
        }
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def start_support_chat(self, support_id: int, user: Dict, max_user_id: int, api):
        """Начать диалог с поддержкой"""
        from utils.keyboard import create_back_keyboard, create_cancel_keyboard
        from utils.states import set_state
        support_user = User.get_by_id(support_id)
        
        if not support_user:
            # Определяем правильную кнопку "Назад" в зависимости от роли
            back_payload = "admin_support" if user.get('role') == 'admin' else "help"
            api.send_message(
                user_id=max_user_id,
                text="❌ Поддержка не найдена",
                attachments=[create_back_keyboard(back_payload)]
            )
            return
        
        set_state(max_user_id, 'waiting_message_to_support', {'support_id': support_id})
        api.send_message(
            user_id=max_user_id,
            text=f"💬 Напишите сообщение для поддержки:\n\n(Отправьте текст сообщения или напишите 'отмена' для отмены)",
            attachments=[create_cancel_keyboard()]
        )
    
    def show_help_common(self, user: Dict, max_user_id: int, api):
        """Показать частые вопросы"""
        from utils.keyboard import create_back_keyboard
        text = "📋 Частые вопросы:\n\n"
        text += "Q: Как изменить роль?\n"
        text += "A: Используйте кнопку 'Выбрать роль' в главном меню\n\n"
        text += "Q: Как отправить сообщение от группы?\n"
        text += "A: Эта функция доступна только старостам группы\n\n"
        text += "Q: Где посмотреть контакты преподавателей?\n"
        text += "A: 'Преподаватели' → 'Список преподавателей'\n\n"
        text += "Q: Как скачать расписание?\n"
        text += "A: 'Расписание' → 'Скачать расписание'"
        
        keyboard = create_back_keyboard("help")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_news(self, user: Dict, max_user_id: int, api):
        """Показать новости для пользователя"""
        from db.models import News
        from utils.keyboard import create_back_keyboard
        news_list = News.get_news_by_role(user['role'], user['id'], limit=20)
        
        if not news_list:
            text = "📢 Новости\n\n"
            text += "⚠️ Новости пока не добавлены.\n"
            text += "Следите за обновлениями!"
            
            keyboard = create_back_keyboard("main_menu")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
            return
        
        # Формируем текст с новостями
        text = "📢 Новости\n\n"
        
        for i, news_item in enumerate(news_list, 1):
            title = news_item.get('title', 'Без названия')
            description = news_item.get('description', '')
            hashtags = news_item.get('hashtags', '')
            created_at = news_item.get('created_at', '')
            
            # Форматируем дату
            if created_at:
                try:
                    from datetime import datetime
                    if isinstance(created_at, str):
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        date_obj = created_at
                    date_str = date_obj.strftime('%d.%m.%Y')
                except:
                    date_str = str(created_at)[:10]
            else:
                date_str = ''
            
            text += f"📌 {title}\n"
            if hashtags:
                hashtag_list = [tag.strip() for tag in hashtags.split(',') if tag.strip()]
                if hashtag_list:
                    text += f"🏷️ {' '.join(['#' + tag for tag in hashtag_list])}\n"
            if date_str:
                text += f"📅 {date_str}\n"
            text += f"{description}\n"
            text += "\n" + "─" * 30 + "\n\n"
        
        keyboard = create_back_keyboard("main_menu")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )

