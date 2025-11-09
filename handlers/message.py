"""Обработчик текстовых сообщений"""
from handlers.base import BaseHandler
from db.models import User, Message
from utils.keyboard import create_main_menu_keyboard, create_back_keyboard, create_cancel_keyboard
from utils.states import get_state, clear_state, is_in_state, get_state_data, set_state, get_user_role
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MessageHandler(BaseHandler):
    """Обработчик текстовых сообщений"""
    
    def can_handle(self, update: Dict[str, Any]) -> bool:
        return update.get('update_type') == 'message_created'
    
    def handle(self, update: Dict[str, Any], api) -> None:
        message = update.get('message', {})
        sender = message.get('sender', {})
        max_user_id = sender.get('user_id')
        first_name = sender.get('first_name', 'Unknown')
        
        if not max_user_id:
            return
        
        # Проверка верификации
        if not self.is_user_verified(max_user_id):
            logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=неверифицированная_попытка_письма")
            api.send_message(
                user_id=max_user_id,
                text="❌ Вы не зарегистрированы в системе. Обратитесь к администрации."
            )
            return
        
        # Получаем данные пользователя
        # Получаем сохраненную роль или используем приоритетную
        saved_role = get_user_role(max_user_id)
        user = User.get_by_max_id(max_user_id, saved_role) if saved_role else User.get_by_max_id(max_user_id)
        if not user:
            return
        
        chat_id = message.get('recipient', {}).get('chat_id')
        body = message.get('body', {})
        text = body.get('text', '').strip()
        message_id = body.get('mid', '')
        
        # Проверка состояния пользователя (FSM)
        user_state = get_state(max_user_id)
        
        if user_state:
            state = user_state.get('state')
            state_data = user_state.get('data', {})
            
            # Обработка состояний отправки сообщений
            if state == 'waiting_message_to_teacher':
                logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=отправка_сообщения_преподавателю")
                self.handle_send_to_teacher(user, max_user_id, text, state_data, api, message_id)
                return
            elif state == 'waiting_broadcast_message':
                logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=рассылка_группе")
                self.handle_broadcast_message(user, max_user_id, text, state_data, api, message_id)
                return
            elif state == 'waiting_message_to_student':
                logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=отправка_сообщения_студенту")
                self.handle_send_to_student(user, max_user_id, text, state_data, api, message_id)
                return
            elif state == 'waiting_group_message':
                logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=отправка_сообщения_от_группы")
                self.handle_group_message(user, max_user_id, text, state_data, api, message_id)
                return
        
        # Обработка команд
        if text.startswith('/'):
            logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=команда_{text}")
            self.handle_command(text, user, chat_id, max_user_id, api)
        else:
            # Обычное сообщение - показываем главное меню
            logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=показ_главного_меню")
            self.show_main_menu(user, chat_id, max_user_id, api)
    
    def handle_command(self, command: str, user: Dict, chat_id: int, 
                      max_user_id: int, api):
        """Обработка команд"""
        if command == '/start':
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=команда_/start")
            self.show_main_menu(user, chat_id, max_user_id, api)
        elif command == '/help':
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=команда_/help")
            self.show_help(user['role'], chat_id, max_user_id, api)
    
    def show_main_menu(self, user: Dict, chat_id: int, max_user_id: int, api):
        """Показать главное меню"""
        from utils.keyboard import create_main_menu_keyboard
        from db.models import User as UserModel
        
        role = user['role']
        
        # Проверяем, есть ли у пользователя несколько ролей
        all_roles = UserModel.get_all_roles(max_user_id)
        has_multiple_roles = len(all_roles) > 1
        
        greeting = {
            'student': f"👋 Привет, {user['fio']}!\n\nВыберите действие:",
            'teacher': f"👋 Здравствуйте, {user['fio']}!\n\nВыберите действие:",
            'admin': f"👋 Администратор {user['fio']}\n\nВыберите действие:"
        }
        
        keyboard = create_main_menu_keyboard(role, has_multiple_roles)
        api.send_message(
            user_id=max_user_id,
            text=greeting.get(role, "Выберите действие:"),
            attachments=[keyboard]
        )
    
    def show_help(self, role: str, chat_id: int, max_user_id: int, api):
        """Показать справку"""
        help_text = {
            'student': (
                "📖 Справка для студентов:\n\n"
                "• Моя группа - просмотр участников группы с контактами\n"
                "• Преподаватели - список ваших преподавателей\n"
                "• Написать преподавателю - отправить сообщение\n\n"
                "Команды:\n"
                "/start - главное меню\n"
                "/help - эта справка"
            ),
            'teacher': (
                "📖 Справка для преподавателей:\n\n"
                "• Мои группы - просмотр ваших групп и студентов\n"
                "• Написать студенту - отправить личное сообщение\n"
                "• Рассылка группе - отправить сообщение всем студентам группы\n\n"
                "Команды:\n"
                "/start - главное меню\n"
                "/help - эта справка"
            ),
            'admin': (
                "📖 Справка для администратора:\n\n"
                "• Написать пользователю - отправить сообщение любому пользователю\n\n"
                "Команды:\n"
                "/start - главное меню\n"
                "/help - эта справка"
            )
        }
        
        text = help_text.get(role, "Справка")
        keyboard = create_main_menu_keyboard(role)
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def handle_send_to_teacher(self, user: Dict, max_user_id: int, text: str, 
                              state_data: Dict, api, message_id: str):
        """Обработать отправку сообщения преподавателю"""
        from db.models import User as UserModel
        
        if text.lower() in ['отмена', 'cancel', '/cancel']:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отмена_отправки_преподавателю")
            clear_state(max_user_id)
            self.show_main_menu(user, None, max_user_id, api)
            return
        
        teacher_id = state_data.get('teacher_id')
        teacher = UserModel.get_by_id(teacher_id)
        
        if teacher:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отправлено_сообщение_преподавателю_{teacher.get('fio', 'Unknown')}")
        
        if not teacher:
            api.send_message(
                user_id=max_user_id,
                text="❌ Преподаватель не найден",
                attachments=[create_back_keyboard()]
            )
            clear_state(max_user_id)
            return
        
        # Отправляем сообщение преподавателю
        result = api.send_message(
            user_id=teacher['max_user_id'],
            text=f"💬 Сообщение от студента {user['fio']}:\n\n{text}"
        )
        
        if result:
            # Получаем message_id из ответа API
            sent_message_id = result.get('message', {}).get('body', {}).get('mid', message_id)
            # Сохраняем в БД
            Message.save_message(
                from_user_id=user['id'],
                to_user_id=teacher_id,
                text=text,
                max_message_id=sent_message_id
            )
            
            api.send_message(
                user_id=max_user_id,
                text=f"✅ Сообщение отправлено преподавателю {teacher['fio']}",
                attachments=[create_main_menu_keyboard(user['role'])]
            )
        else:
            api.send_message(
                user_id=max_user_id,
                text="❌ Ошибка при отправке сообщения. Попробуйте позже.",
                attachments=[create_back_keyboard()]
            )
        
        clear_state(max_user_id)
    
    def handle_send_to_student(self, user: Dict, max_user_id: int, text: str,
                               state_data: Dict, api, message_id: str):
        """Обработать отправку сообщения студенту"""
        from db.models import User as UserModel
        
        if text.lower() in ['отмена', 'cancel', '/cancel']:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отмена_отправки_студенту")
            clear_state(max_user_id)
            self.show_main_menu(user, None, max_user_id, api)
            return
        
        student_id = state_data.get('student_id')
        student = UserModel.get_by_id(student_id)
        
        if student:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отправлено_сообщение_студенту_{student.get('fio', 'Unknown')}")
        
        if not student:
            api.send_message(
                user_id=max_user_id,
                text="❌ Студент не найден",
                attachments=[create_back_keyboard()]
            )
            clear_state(max_user_id)
            return
        
        # Отправляем сообщение студенту
        result = api.send_message(
            user_id=student['max_user_id'],
            text=f"💬 Сообщение от преподавателя {user['fio']}:\n\n{text}"
        )
        
        if result:
            # Получаем message_id из ответа API
            sent_message_id = result.get('message', {}).get('body', {}).get('mid', message_id)
            # Сохраняем в БД
            Message.save_message(
                from_user_id=user['id'],
                to_user_id=student_id,
                text=text,
                max_message_id=sent_message_id
            )
            
            api.send_message(
                user_id=max_user_id,
                text=f"✅ Сообщение отправлено студенту {student['fio']}",
                attachments=[create_main_menu_keyboard(user['role'])]
            )
        else:
            api.send_message(
                user_id=max_user_id,
                text="❌ Ошибка при отправке сообщения. Попробуйте позже.",
                attachments=[create_back_keyboard()]
            )
        
        clear_state(max_user_id)
    
    def handle_broadcast_message(self, user: Dict, max_user_id: int, text: str,
                                state_data: Dict, api, message_id: str):
        """Обработать рассылку группе"""
        from db.models import Group
        
        if text.lower() in ['отмена', 'cancel', '/cancel']:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отмена_рассылки")
            clear_state(max_user_id)
            self.show_main_menu(user, None, max_user_id, api)
            return
        
        group_id = state_data.get('group_id')
        group = Group.get_by_id(group_id)
        
        if group:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=рассылка_группе_{group.get('name', 'Unknown')}")
        
        if not group:
            api.send_message(
                user_id=max_user_id,
                text="❌ Группа не найдена",
                attachments=[create_back_keyboard()]
            )
            clear_state(max_user_id)
            return
        
        # Получаем всех студентов группы
        students = Group.get_group_members(group_id)
        
        if not students:
            api.send_message(
                user_id=max_user_id,
                text="❌ В группе нет студентов",
                attachments=[create_back_keyboard()]
            )
            clear_state(max_user_id)
            return
        
        # Отправляем сообщение всем студентам
        success_count = 0
        for student in students:
            result = api.send_message(
                user_id=student['max_user_id'],
                text=f"📢 Сообщение от преподавателя {user['fio']} (группа {group['name']}):\n\n{text}"
            )
            if result:
                success_count += 1
                # Получаем message_id из ответа API
                sent_message_id = result.get('message', {}).get('body', {}).get('mid', message_id)
                # Сохраняем в БД
                Message.save_message(
                    from_user_id=user['id'],
                    to_user_id=student['id'],
                    text=text,
                    max_message_id=sent_message_id,
                    group_id=group_id
                )
        
        api.send_message(
            user_id=max_user_id,
            text=f"✅ Сообщение отправлено {success_count} из {len(students)} студентов группы {group['name']}",
            attachments=[create_main_menu_keyboard(user['role'])]
        )
        
        clear_state(max_user_id)
    
    def handle_group_message(self, user: Dict, max_user_id: int, text: str,
                            state_data: Dict, api, message_id: str):
        """Обработать отправку сообщения от имени группы"""
        from db.models import Group, Teacher
        
        if text.lower() in ['отмена', 'cancel', '/cancel']:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отмена_отправки_от_группы")
            clear_state(max_user_id)
            self.show_main_menu(user, None, max_user_id, api)
            return
        
        group_id = state_data.get('group_id')
        teacher_id = state_data.get('teacher_id')
        group = Group.get_by_id(group_id)
        teacher = User.get_by_id(teacher_id)
        
        if group and teacher:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отправлено_сообщение_от_группы_{group.get('name', 'Unknown')}_преподавателю_{teacher.get('fio', 'Unknown')}")
        
        if not group or not teacher:
            api.send_message(
                user_id=max_user_id,
                text="❌ Ошибка: группа или преподаватель не найдены",
                attachments=[create_back_keyboard()]
            )
            clear_state(max_user_id)
            return
        
        # Отправляем сообщение преподавателю от имени группы
        result = api.send_message(
            user_id=teacher['max_user_id'],
            text=f"💬 Сообщение от группы {group['name']} (староста: {user['fio']}):\n\n{text}"
        )
        
        if result:
            # Получаем message_id из ответа API
            sent_message_id = result.get('message', {}).get('body', {}).get('mid', message_id)
            # Сохраняем в БД
            Message.save_message(
                from_user_id=user['id'],
                to_user_id=teacher_id,
                text=text,
                max_message_id=sent_message_id,
                group_id=group_id
            )
            
            api.send_message(
                user_id=max_user_id,
                text=f"✅ Сообщение отправлено преподавателю {teacher['fio']} от имени группы {group['name']}",
                attachments=[create_main_menu_keyboard(user['role'])]
            )
        else:
            api.send_message(
                user_id=max_user_id,
                text="❌ Ошибка при отправке сообщения. Попробуйте позже.",
                attachments=[create_back_keyboard()]
            )
        
        clear_state(max_user_id)

