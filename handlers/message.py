"""Обработчик текстовых сообщений"""
from handlers.base import BaseHandler
from db.models import User, Message, SupportTicket, FAQ
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
            elif state == 'waiting_message_to_support':
                logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=отправка_сообщения_в_поддержку")
                self.handle_send_to_support(user, max_user_id, text, state_data, api, message_id)
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
            elif state == 'waiting_message_to_student_student':
                logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=отправка_сообщения_студенту_студенту")
                self.handle_send_to_student_student(user, max_user_id, text, state_data, api, message_id)
                return
            elif state == 'waiting_broadcast_headmen':
                logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=рассылка_старостам")
                self.handle_broadcast_headmen(user, max_user_id, text, state_data, api, message_id)
                return
            elif state == 'admin_schedule_edit':
                logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=редактирование_расписания")
                self.handle_edit_schedule(user, max_user_id, text, api, message_id)
                return
            elif state.startswith('admin_'):
                logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=админ_{state}")
                self.handle_admin_state(user, max_user_id, text, state, state_data, api, message_id)
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
        from utils.keyboard import create_help_menu_keyboard, create_main_menu_keyboard
        
        if role == 'student':
            keyboard = create_help_menu_keyboard('student')
            api.send_message(
                user_id=max_user_id,
                text="❓ Помощь\n\nВыберите раздел:",
                attachments=[keyboard]
            )
            return
        elif role == 'teacher':
            keyboard = create_help_menu_keyboard('teacher')
            api.send_message(
                user_id=max_user_id,
                text="❓ Помощь\n\nВыберите раздел:",
                attachments=[keyboard]
            )
            return
        
        help_text = {
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
    
    def handle_send_to_support(self, user: Dict, max_user_id: int, text: str,
                               state_data: Dict, api, message_id: str):
        """Обработать отправку сообщения в поддержку"""
        from db.models import User as UserModel, SupportTicket, Message
        
        if text.lower() in ['отмена', 'cancel', '/cancel']:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отмена_отправки_в_поддержку")
            clear_state(max_user_id)
            # Если администратор - возвращаем в меню поддержки, иначе в главное меню
            if user.get('role') == 'admin':
                from handlers.callback import CallbackHandler
                callback_handler = CallbackHandler()
                callback_handler.show_admin_support_menu(user, max_user_id, api)
            else:
                self.show_main_menu(user, None, max_user_id, api)
            return
        
        support_id = state_data.get('support_id')
        support_user = UserModel.get_by_id(support_id)
        
        if support_user:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отправлено_сообщение_в_поддержку_{support_user.get('fio', 'Unknown')}")
        
        if not support_user:
            api.send_message(
                user_id=max_user_id,
                text="❌ Поддержка не найдена",
                attachments=[create_back_keyboard()]
            )
            clear_state(max_user_id)
            return
        
        # Создаем тикет автоматически
        subject = text[:100] if len(text) > 100 else text  # Тема - первые 100 символов сообщения
        ticket_id = SupportTicket.create_ticket(user['id'], subject, text)
        
        if not ticket_id:
            logger.error(f"Ошибка при создании тикета для пользователя {user['id']}")
            api.send_message(
                user_id=max_user_id,
                text="❌ Ошибка при создании обращения. Попробуйте позже.",
                attachments=[create_back_keyboard()]
            )
            clear_state(max_user_id)
            return
        
        logger.info(f"Создан тикет #{ticket_id} для пользователя {user['id']}")
        
        # Отправляем сообщение поддержке
        result = api.send_message(
            user_id=support_user['max_user_id'],
            text=f"💬 Сообщение от {user['fio']} (Тикет #{ticket_id}):\n\n{text}"
        )
        
        if result:
            # Получаем message_id из ответа API
            sent_message_id = result.get('message', {}).get('body', {}).get('mid', message_id)
            # Сохраняем в БД
            Message.save_message(
                from_user_id=user['id'],
                to_user_id=support_id,
                text=text,
                max_message_id=sent_message_id
            )
            
            # Определяем правильную кнопку "Назад" в зависимости от роли
            if user.get('role') == 'admin':
                from utils.keyboard import create_back_keyboard
                back_keyboard = create_back_keyboard("admin_support")
            else:
                back_keyboard = create_main_menu_keyboard(user['role'])
            
            api.send_message(
                user_id=max_user_id,
                text=f"✅ Сообщение отправлено в поддержку\n\n"
                     f"📋 Тикет создан: #{ticket_id}\n"
                     f"📊 Статус: На рассмотрении",
                attachments=[back_keyboard]
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
    
    def handle_send_to_student_student(self, user: Dict, max_user_id: int, text: str,
                                      state_data: Dict, api, message_id: str):
        """Обработать отправку сообщения студентом студенту"""
        from db.models import User as UserModel
        
        if text.lower() in ['отмена', 'cancel', '/cancel']:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отмена_отправки_студенту_студенту")
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
                attachments=[create_back_keyboard("menu_group")]
            )
            clear_state(max_user_id)
            return
        
        # Отправляем сообщение студенту
        result = api.send_message(
            user_id=student['max_user_id'],
            text=f"💬 Сообщение от {user['fio']}:\n\n{text}"
        )
        
        if result:
            api.send_message(
                user_id=max_user_id,
                text=f"✅ Сообщение отправлено {student['fio']}",
                attachments=[create_main_menu_keyboard(user['role'])]
            )
        else:
            api.send_message(
                user_id=max_user_id,
                text="❌ Ошибка при отправке сообщения. Попробуйте позже.",
                attachments=[create_back_keyboard("menu_group")]
            )
        
        clear_state(max_user_id)
    
    def handle_broadcast_headmen(self, user: Dict, max_user_id: int, text: str,
                                 state_data: Dict, api, message_id: str):
        """Обработать рассылку старостам"""
        from db.models import Teacher
        
        if text.lower() in ['отмена', 'cancel', '/cancel']:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отмена_рассылки_старостам")
            clear_state(max_user_id)
            self.show_main_menu(user, None, max_user_id, api)
            return
        
        # Получаем всех старост групп преподавателя
        headmen = Teacher.get_teacher_headmen(user['id'])
        
        if not headmen:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет старост в группах",
                attachments=[create_back_keyboard("menu_headmen")]
            )
            clear_state(max_user_id)
            return
        
        # Отправляем сообщение всем старостам
        success_count = 0
        for headman in headmen:
            result = api.send_message(
                user_id=headman['max_user_id'],
                text=f"📢 Сообщение от преподавателя {user['fio']} (старостам):\n\n{text}"
            )
            if result:
                success_count += 1
        
        api.send_message(
            user_id=max_user_id,
            text=f"✅ Сообщение отправлено {success_count} из {len(headmen)} старостам",
            attachments=[create_main_menu_keyboard(user['role'])]
        )
        
        clear_state(max_user_id)
    
    def handle_admin_state(self, user: Dict, max_user_id: int, text: str, state: str,
                          state_data: Dict, api, message_id: str):
        """Обработать состояния администратора"""
        from db.models import User as UserModel, Group
        
        if text.lower() in ['отмена', 'cancel', '/cancel']:
            clear_state(max_user_id)
            self.show_main_menu(user, None, max_user_id, api)
            return
        
        if state == 'admin_student_add':
            # Формат: max_user_id, ФИО, телефон, email
            parts = [p.strip() for p in text.split(',')]
            if len(parts) < 2:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Неверный формат. Используйте: max_user_id, ФИО, телефон, email",
                    attachments=[create_cancel_keyboard()]
                )
                return
            
            try:
                max_user_id_student = int(parts[0])
                fio = parts[1]
                phone = parts[2] if len(parts) > 2 else None
                email = parts[3] if len(parts) > 3 else None
                
                user_id = UserModel.create_user(max_user_id_student, fio, 'student', phone, email)
                if user_id:
                    api.send_message(
                        user_id=max_user_id,
                        text=f"✅ Студент {fio} добавлен (ID: {user_id})",
                        attachments=[create_main_menu_keyboard(user['role'])]
                    )
                else:
                    api.send_message(
                        user_id=max_user_id,
                        text="❌ Ошибка при добавлении студента",
                        attachments=[create_cancel_keyboard()]
                    )
            except ValueError:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Неверный формат max_user_id. Должно быть число.",
                    attachments=[create_cancel_keyboard()]
                )
            clear_state(max_user_id)
        
        elif state == 'admin_student_edit':
            # Формат: ФИО, телефон, email
            student_id = state_data.get('student_id')
            if not student_id:
                clear_state(max_user_id)
                return
            
            parts = [p.strip() for p in text.split(',')]
            fio = parts[0] if len(parts) > 0 else None
            phone = parts[1] if len(parts) > 1 else None
            email = parts[2] if len(parts) > 2 else None
            
            if UserModel.update_user(student_id, fio, phone, email):
                api.send_message(
                    user_id=max_user_id,
                    text="✅ Данные студента обновлены",
                    attachments=[create_main_menu_keyboard(user['role'])]
                )
            else:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Ошибка при обновлении данных",
                    attachments=[create_cancel_keyboard()]
                )
            clear_state(max_user_id)
        
        elif state == 'admin_teacher_add':
            # Формат: max_user_id, ФИО, телефон, email
            parts = [p.strip() for p in text.split(',')]
            if len(parts) < 2:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Неверный формат. Используйте: max_user_id, ФИО, телефон, email",
                    attachments=[create_cancel_keyboard()]
                )
                return
            
            try:
                max_user_id_teacher = int(parts[0])
                fio = parts[1]
                phone = parts[2] if len(parts) > 2 else None
                email = parts[3] if len(parts) > 3 else None
                
                user_id = UserModel.create_user(max_user_id_teacher, fio, 'teacher', phone, email)
                if user_id:
                    api.send_message(
                        user_id=max_user_id,
                        text=f"✅ Преподаватель {fio} добавлен (ID: {user_id})",
                        attachments=[create_main_menu_keyboard(user['role'])]
                    )
                else:
                    api.send_message(
                        user_id=max_user_id,
                        text="❌ Ошибка при добавлении преподавателя",
                        attachments=[create_cancel_keyboard()]
                    )
            except ValueError:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Неверный формат max_user_id. Должно быть число.",
                    attachments=[create_cancel_keyboard()]
                )
            clear_state(max_user_id)
        
        elif state == 'admin_teacher_edit':
            # Формат: ФИО, телефон, email
            teacher_id = state_data.get('teacher_id')
            if not teacher_id:
                clear_state(max_user_id)
                return
            
            parts = [p.strip() for p in text.split(',')]
            fio = parts[0] if len(parts) > 0 else None
            phone = parts[1] if len(parts) > 1 else None
            email = parts[2] if len(parts) > 2 else None
            
            if UserModel.update_user(teacher_id, fio, phone, email):
                api.send_message(
                    user_id=max_user_id,
                    text="✅ Данные преподавателя обновлены",
                    attachments=[create_main_menu_keyboard(user['role'])]
                )
            else:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Ошибка при обновлении данных",
                    attachments=[create_cancel_keyboard()]
                )
            clear_state(max_user_id)
        
        elif state == 'admin_broadcast_all_students':
            # Рассылка всем студентам
            if text.lower() in ['отмена', 'cancel', '/cancel']:
                logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отмена_рассылки_студентам")
                clear_state(max_user_id)
                from handlers.callback import CallbackHandler
                callback_handler = CallbackHandler()
                callback_handler.show_admin_broadcasts_menu(user, max_user_id, api)
                return
            
            # Получаем всех студентов
            students = UserModel.get_all_students()
            
            # Отправляем сообщение всем студентам
            sent_count = 0
            failed_count = 0
            
            for student in students:
                try:
                    result = api.send_message(
                        user_id=student['max_user_id'],
                        text=f"📢 Сообщение от администрации:\n\n{text}"
                    )
                    if result:
                        sent_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Ошибка при отправке сообщения студенту {student.get('max_user_id')}: {e}")
                    failed_count += 1
            
            clear_state(max_user_id)
            api.send_message(
                user_id=max_user_id,
                text=f"✅ Рассылка завершена\n\n"
                     f"📤 Отправлено студентам: {sent_count}\n"
                     f"❌ Ошибок: {failed_count}",
                attachments=[create_back_keyboard("admin_broadcasts")]
            )
        elif state == 'admin_broadcast_all_teachers':
            # Рассылка всем преподавателям
            if text.lower() in ['отмена', 'cancel', '/cancel']:
                logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отмена_рассылки_преподавателям")
                clear_state(max_user_id)
                from handlers.callback import CallbackHandler
                callback_handler = CallbackHandler()
                callback_handler.show_admin_broadcasts_menu(user, max_user_id, api)
                return
            
            # Получаем всех преподавателей
            from db.models import Teacher
            teachers = Teacher.get_all_teachers()
            
            # Отправляем сообщение всем преподавателям
            sent_count = 0
            failed_count = 0
            
            for teacher in teachers:
                try:
                    result = api.send_message(
                        user_id=teacher['max_user_id'],
                        text=f"📢 Сообщение от администрации:\n\n{text}"
                    )
                    if result:
                        sent_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Ошибка при отправке сообщения преподавателю {teacher.get('max_user_id')}: {e}")
                    failed_count += 1
            
            clear_state(max_user_id)
            api.send_message(
                user_id=max_user_id,
                text=f"✅ Рассылка завершена\n\n"
                     f"📤 Отправлено преподавателям: {sent_count}\n"
                     f"❌ Ошибок: {failed_count}",
                attachments=[create_back_keyboard("admin_broadcasts")]
            )
        elif state in ['admin_support_contact', 'support_contact', 'waiting_message_from_support']:
            # Отправка сообщения пользователю из обращения (для admin и support)
            user_id = state_data.get('user_id')
            ticket_id = state_data.get('ticket_id')
            if user_id:
                target_user = UserModel.get_by_id(user_id)
                if target_user:
                    from api.max_api import MaxAPI
                    max_api = MaxAPI()
                    try:
                        max_api.send_message(
                            user_id=target_user['max_user_id'],
                            text=f"💬 Ответ от поддержки:\n\n{text}"
                        )
                        # Определяем правильный payload для кнопки "Назад"
                        back_payload = f"admin_support_ticket_{ticket_id}" if state == 'admin_support_contact' else f"support_ticket_{ticket_id}"
                        api.send_message(
                            user_id=max_user_id,
                            text=f"✅ Сообщение отправлено пользователю {target_user.get('fio', '')}",
                            attachments=[create_back_keyboard(back_payload)]
                        )
                    except Exception as e:
                        logger.error(f"Ошибка при отправке сообщения: {e}")
                        back_payload = f"admin_support_ticket_{ticket_id}" if state == 'admin_support_contact' else f"support_ticket_{ticket_id}"
                        api.send_message(
                            user_id=max_user_id,
                            text="❌ Ошибка при отправке сообщения",
                            attachments=[create_back_keyboard(back_payload)]
                        )
            clear_state(max_user_id)
        elif state == 'admin_support_faq_add':
            # Добавление FAQ
            # Формат: Вопрос\nОтвет
            lines = text.split('\n', 1)
            if len(lines) < 2:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Неверный формат. Используйте:\nВопрос\nОтвет",
                    attachments=[create_cancel_keyboard()]
                )
                return
            
            question = lines[0].strip()
            answer = lines[1].strip()
            
            admin_user = UserModel.get_by_max_id(max_user_id, role='admin')
            created_by = admin_user['id'] if admin_user else None
            
            faq_id = FAQ.create_faq(question, answer, category='general', created_by=created_by)
            if faq_id:
                api.send_message(
                    user_id=max_user_id,
                    text="✅ FAQ добавлен",
                    attachments=[create_back_keyboard("admin_support_faq")]
                )
            else:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Ошибка при добавлении FAQ",
                    attachments=[create_cancel_keyboard()]
                )
            clear_state(max_user_id)
    
    def handle_edit_schedule(self, user: Dict, max_user_id: int, text: str, api, message_id: str):
        """Обработать редактирование расписания"""
        if text.lower() in ['отмена', 'cancel', '/cancel']:
            logger.info(f"[USER] user_id={max_user_id}, first_name={user.get('fio', 'Unknown')}, action=отмена_редактирования_расписания")
            clear_state(max_user_id)
            from handlers.callback import CallbackHandler
            callback_handler = CallbackHandler()
            callback_handler.show_main_menu(user, max_user_id, api)
            return
        
        # Проверяем формат URL
        if not text.startswith('http://') and not text.startswith('https://'):
            api.send_message(
                user_id=max_user_id,
                text="❌ Неверный формат URL. URL должен начинаться с http:// или https://\n\nПопробуйте еще раз или напишите 'отмена'.",
                attachments=[create_cancel_keyboard()]
            )
            return
        
        # Сохраняем URL в переменную окружения
        import os
        os.environ['SCHEDULE_API_URL'] = text
        
        # Обновляем глобальную переменную в handlers/callback.py
        import handlers.callback as callback_module
        callback_module.SCHEDULE_API_URL = text
        
        clear_state(max_user_id)
        api.send_message(
            user_id=max_user_id,
            text=f"✅ URL API расписания обновлен:\n{text}\n\n"
                 f"⚠️ Изменения вступят в силу после перезапуска бота.",
            attachments=[create_back_keyboard("main_menu")]
        )

