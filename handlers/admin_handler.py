"""Обработчики для администрации"""
from typing import Dict, Any
from db.models import User, Group, Teacher, SupportTicket, FAQ
from db.connection import execute_query
from utils.keyboard import (
    create_admin_students_menu_keyboard, create_admin_teachers_menu_keyboard,
    create_admin_groups_menu_keyboard, create_admin_broadcasts_menu_keyboard,
    create_admin_reports_menu_keyboard, create_admin_help_menu_keyboard,
    create_admin_support_menu_keyboard, create_support_tickets_status_keyboard,
    create_support_tickets_list_keyboard, create_support_ticket_actions_keyboard,
    create_faq_list_keyboard,
    create_back_keyboard, create_cancel_keyboard
)
from utils.states import set_state, clear_state, get_state
import logging

logger = logging.getLogger(__name__)


class AdminHandler:
    """Обработчики для администрации"""
    
    def show_admin_students_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню управления студентами"""
        text = "👨‍🎓 Управление студентами\n\n"
        text += "📱 Данный функционал доступен в мини-приложении.\n"
        
        keyboard = create_back_keyboard("main_menu")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_admin_teachers_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню управления преподавателями"""
        text = "👨‍🏫 Управление преподавателями\n\n"
        text += "📱 Данный функционал доступен в мини-приложении.\n"
        
        keyboard = create_back_keyboard("main_menu")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_admin_groups_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню управления группами"""
        keyboard = create_admin_groups_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="👥 Управление группами\n\nВыберите действие:",
            attachments=[keyboard]
        )
    
    def show_admin_broadcasts_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню рассылок"""
        keyboard = create_admin_broadcasts_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="📢 Рассылки\n\nВыберите действие:",
            attachments=[keyboard]
        )
    
    def show_admin_reports_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню отчетов"""
        keyboard = create_admin_reports_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="📊 Отчеты\n\nВыберите раздел:",
            attachments=[keyboard]
        )
    
    def show_admin_support_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню поддержки для администратора"""
        keyboard = create_admin_support_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="💬 Поддержка\n\nВыберите раздел:",
            attachments=[keyboard]
        )
    
    def handle_admin_student_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия со студентами"""
        text = "👨‍🎓 Управление студентами\n\n"
        text += "📱 Данный функционал доступен в мини-приложении.\n"
        
        keyboard = create_back_keyboard("main_menu")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def handle_admin_teacher_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия с преподавателями"""
        text = "👨‍🏫 Управление преподавателями\n\n"
        text += "📱 Данный функционал доступен в мини-приложении.\n"
        
        keyboard = create_back_keyboard("main_menu")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def handle_admin_group_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия с группами"""
        from utils.keyboard import create_groups_list_keyboard, create_students_list_keyboard, create_teachers_list_keyboard
        from utils.states import set_state, get_state, clear_state
        action = payload.replace('admin_group_', '')
        
        if action == 'view':
            text = "👥 Просмотр состава группы\n\n"
            text += "📱 Данный функционал доступен в мини-приложении.\n"
            keyboard = create_back_keyboard("admin_groups")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
            return
        elif action.startswith('view_select_'):
            text = "👥 Просмотр состава группы\n\n"
            text += "📱 Данный функционал доступен в мини-приложении.\n"
            keyboard = create_back_keyboard("admin_groups")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
            return
        elif action == 'add_student':
            groups = Group.get_all_groups()
            if not groups:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет групп в системе",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            keyboard = create_groups_list_keyboard(groups, prefix="admin_group_add_student_select")
            api.send_message(
                user_id=max_user_id,
                text="➕ Выберите группу для добавления студента:",
                attachments=[keyboard]
            )
        elif action == 'remove_student':
            groups = Group.get_all_groups()
            if not groups:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет групп в системе",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            keyboard = create_groups_list_keyboard(groups, prefix="admin_group_remove_student_select")
            api.send_message(
                user_id=max_user_id,
                text="➖ Выберите группу для удаления студента:",
                attachments=[keyboard]
            )
        elif action == 'assign_teacher':
            groups = Group.get_all_groups()
            if not groups:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет групп в системе",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            keyboard = create_groups_list_keyboard(groups, prefix="admin_group_assign_teacher_select")
            api.send_message(
                user_id=max_user_id,
                text="👨‍🏫 Выберите группу для привязки преподавателя:",
                attachments=[keyboard]
            )
        elif action.startswith('add_student_select_'):
            group_id = int(action.replace('add_student_select_', ''))
            students = User.get_all_students()
            if not students:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет студентов в системе",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            set_state(max_user_id, 'admin_group_add_student', {'group_id': group_id})
            keyboard = create_students_list_keyboard(students, prefix="admin_group_add_student_to")
            api.send_message(
                user_id=max_user_id,
                text="➕ Выберите студента для добавления:",
                attachments=[keyboard]
            )
        elif action.startswith('add_student_to_'):
            student_id = int(action.replace('add_student_to_', ''))
            state_data = get_state(max_user_id)
            if state_data and state_data.get('state') == 'admin_group_add_student':
                group_id = state_data.get('data', {}).get('group_id')
                if group_id:
                    User.assign_user_to_group(student_id, group_id)
                    student = User.get_by_id(student_id)
                    group = Group.get_by_id(group_id)
                    api.send_message(
                        user_id=max_user_id,
                        text=f"✅ Студент {student['fio'] if student else ''} добавлен в группу {group['name'] if group else ''}",
                        attachments=[create_back_keyboard("admin_groups")]
                    )
                    clear_state(max_user_id)
        elif action.startswith('remove_student_select_'):
            group_id = int(action.replace('remove_student_select_', ''))
            members = Group.get_group_members(group_id)
            if not members:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ В группе нет студентов",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            set_state(max_user_id, 'admin_group_remove_student', {'group_id': group_id})
            buttons = []
            for member in members:
                buttons.append([{
                    "type": "callback",
                    "text": f"{'⭐ ' if member.get('is_headman') else ''}{member['fio']}",
                    "payload": f"admin_group_remove_student_from_{member['id']}"
                }])
            buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "admin_groups"}])
            keyboard = {
                "type": "inline_keyboard",
                "payload": {"buttons": buttons}
            }
            api.send_message(
                user_id=max_user_id,
                text="➖ Выберите студента для удаления из группы:",
                attachments=[keyboard]
            )
        elif action.startswith('remove_student_from_'):
            student_id = int(action.replace('remove_student_from_', ''))
            state_data = get_state(max_user_id)
            if state_data and state_data.get('state') == 'admin_group_remove_student':
                group_id = state_data.get('data', {}).get('group_id')
                if group_id:
                    User.remove_user_from_group(student_id, group_id)
                    student = User.get_by_id(student_id)
                    group = Group.get_by_id(group_id)
                    api.send_message(
                        user_id=max_user_id,
                        text=f"✅ Студент {student['fio'] if student else ''} удален из группы {group['name'] if group else ''}",
                        attachments=[create_back_keyboard("admin_groups")]
                    )
                    clear_state(max_user_id)
        elif action.startswith('assign_teacher_select_'):
            group_id = int(action.replace('assign_teacher_select_', ''))
            teachers = Teacher.get_all_teachers()
            if not teachers:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет преподавателей в системе",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            set_state(max_user_id, 'admin_group_assign_teacher', {'group_id': group_id})
            keyboard = create_teachers_list_keyboard(teachers, prefix="admin_group_assign_teacher_to")
            api.send_message(
                user_id=max_user_id,
                text="👨‍🏫 Выберите преподавателя:",
                attachments=[keyboard]
            )
        elif action.startswith('assign_teacher_to_'):
            teacher_id = int(action.replace('assign_teacher_to_', ''))
            state_data = get_state(max_user_id)
            if state_data and state_data.get('state') == 'admin_group_assign_teacher':
                group_id = state_data.get('data', {}).get('group_id')
                if group_id:
                    User.assign_teacher_to_group(teacher_id, group_id)
                    teacher = User.get_by_id(teacher_id)
                    group = Group.get_by_id(group_id)
                    api.send_message(
                        user_id=max_user_id,
                        text=f"✅ Преподаватель {teacher['fio'] if teacher else ''} привязан к группе {group['name'] if group else ''}",
                        attachments=[create_back_keyboard("admin_groups")]
                    )
                    clear_state(max_user_id)
    
    def handle_admin_broadcast_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия с рассылками"""
        action = payload.replace('admin_broadcast_', '')
        
        if action == 'all_students':
            set_state(max_user_id, 'admin_broadcast_all_students', {})
            api.send_message(
                user_id=max_user_id,
                text="📢 Рассылка всем студентам\n\nОтправьте сообщение, которое будет доставлено всем студентам:",
                attachments=[create_cancel_keyboard()]
            )
        elif action == 'all_teachers':
            set_state(max_user_id, 'admin_broadcast_all_teachers', {})
            api.send_message(
                user_id=max_user_id,
                text="📢 Рассылка всем преподавателям\n\nОтправьте сообщение, которое будет доставлено всем преподавателям:",
                attachments=[create_cancel_keyboard()]
            )
    
    def handle_admin_report_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия с отчетами"""
        action = payload.replace('admin_report_', '')
        
        if action == 'messages':
            # Копируем статистику по сообщениям у поддержки
            from db.models import Message
            
            # Общая статистика по сообщениям
            total_query = "SELECT COUNT(*) as count FROM messages"
            total = execute_query(total_query, (), fetch_one=True)
            total_count = total.get('count', 0) if total else 0
            
            # Непрочитанные сообщения
            unread_query = "SELECT COUNT(*) as count FROM messages WHERE status = 'unread'"
            unread = execute_query(unread_query, (), fetch_one=True)
            unread_count = unread.get('count', 0) if unread else 0
            
            # Прочитанные сообщения
            read_count = total_count - unread_count
            
            # Сообщения по ролям отправителей
            students_query = """
                SELECT COUNT(*) as count 
                FROM messages m
                JOIN users u ON m.from_user_id = u.id
                WHERE u.role = 'student'
            """
            students_msg = execute_query(students_query, (), fetch_one=True)
            students_count = students_msg.get('count', 0) if students_msg else 0
            
            teachers_query = """
                SELECT COUNT(*) as count 
                FROM messages m
                JOIN users u ON m.from_user_id = u.id
                WHERE u.role = 'teacher'
            """
            teachers_msg = execute_query(teachers_query, (), fetch_one=True)
            teachers_count = teachers_msg.get('count', 0) if teachers_msg else 0
            
            text = "💬 Статистика по сообщениям\n\n"
            text += f"📊 Всего сообщений: {total_count}\n"
            text += f"✅ Прочитано: {read_count}\n"
            text += f"📬 Непрочитано: {unread_count}\n\n"
            text += f"👨‍🎓 От студентов: {students_count}\n"
            text += f"👨‍🏫 От преподавателей: {teachers_count}\n"
            
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[create_back_keyboard("admin_reports")]
            )
        elif action == 'users':
            students = User.get_all_students()
            teachers = Teacher.get_all_teachers()
            text = "👥 Отчеты по пользователям\n\n"
            text += f"👨‍🎓 Студентов: {len(students)}\n"
            text += f"👨‍🏫 Преподавателей: {len(teachers)}\n"
            text += f"📊 Всего пользователей: {len(students) + len(teachers)}"
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[create_back_keyboard("admin_reports")]
            )
    
    def handle_admin_help_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия помощи для администратора"""
        action = payload.replace('admin_help_', '')
        
        if action == 'instructions':
            text = "📖 Инструкции по работе с ботом\n\n"
            text += "👨‍🎓 Управление студентами:\n"
            text += "• Добавление: отправьте данные в формате max_user_id, ФИО, телефон, email\n"
            text += "• Редактирование: выберите студента и отправьте новые данные\n"
            text += "• Удаление: выберите студента для удаления\n\n"
            text += "👨‍🏫 Управление преподавателями:\n"
            text += "• Аналогично управлению студентами\n\n"
            text += "👥 Управление группами:\n"
            text += "• Просмотр состава группы\n"
            text += "• Добавление/удаление студентов\n"
            text += "• Привязка преподавателей\n\n"
            text += "📢 Рассылки:\n"
            text += "• Массовые уведомления всем пользователям или группам"
            
            # Создаем кнопку "Назад" которая вернет в меню помощи
            buttons = [[{"type": "callback", "text": "◀️ Назад", "payload": "help"}]]
            keyboard = {
                "type": "inline_keyboard",
                "payload": {"buttons": buttons}
            }
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
    
    def handle_admin_support_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия поддержки для администратора"""
        from db.models import FAQ
        from utils.states import set_state
        action = payload.replace('admin_support_', '')
        
        if action == 'tickets':
            keyboard = create_support_tickets_status_keyboard(role='admin')
            api.send_message(
                user_id=max_user_id,
                text="📋 Запросы в поддержку\n\nВыберите статус:",
                attachments=[keyboard]
            )
        elif action in ['tickets_new', 'tickets_in_progress', 'tickets_resolved', 'tickets_all']:
            status_map = {
                'tickets_new': 'new',
                'tickets_in_progress': 'in_progress',
                'tickets_resolved': 'resolved',
                'tickets_all': None
            }
            status = status_map.get(action)
            tickets = SupportTicket.get_tickets(status=status)
            
            if not tickets:
                status_text = {
                    'new': 'новых',
                    'in_progress': 'в работе',
                    'resolved': 'решенных',
                    None: ''
                }.get(status, '')
                api.send_message(
                    user_id=max_user_id,
                    text=f"❌ Нет {status_text} обращений",
                    attachments=[create_support_tickets_status_keyboard(role='admin')]
                )
                return
            
            keyboard = create_support_tickets_list_keyboard(tickets, prefix="support_ticket", back_payload="admin_support_tickets")
            status_text = {
                'new': '🆕 Новые',
                'in_progress': '🔄 В работе',
                'resolved': '✅ Решено',
                None: '📋 Все'
            }.get(status, '📋')
            api.send_message(
                user_id=max_user_id,
                text=f"{status_text} обращения ({len(tickets)}):",
                attachments=[keyboard]
            )
        elif action.startswith('ticket_'):
            ticket_id = int(action.split('_')[-1])
            ticket = SupportTicket.get_ticket_by_id(ticket_id)
            
            if not ticket:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Обращение не найдено",
                    attachments=[create_support_tickets_status_keyboard(role='admin')]
                )
                return
            
            status_emoji = {
                'new': '🆕',
                'in_progress': '🔄',
                'resolved': '✅'
            }.get(ticket.get('status', 'new'), '📋')
            
            status_text = {
                'new': 'Новое',
                'in_progress': 'В работе',
                'resolved': 'Решено'
            }.get(ticket.get('status', 'new'), 'Неизвестно')
            
            text = f"{status_emoji} Обращение #{ticket['id']}\n\n"
            text += f"👤 Пользователь: {ticket.get('fio', 'Неизвестно')}\n"
            text += f"📋 Статус: {status_text}\n"
            if ticket.get('admin_fio'):
                text += f"👨‍💼 Администратор: {ticket.get('admin_fio')}\n"
            text += f"📅 Создано: {ticket.get('created_at', 'Неизвестно')}\n\n"
            text += f"📝 Тема: {ticket.get('subject', 'Без темы')}\n\n"
            text += f"💬 Сообщение:\n{ticket.get('message', '')}\n"
            
            if ticket.get('response_time'):
                text += f"\n⏱ Время реакции: {ticket['response_time']} мин."
            
            keyboard = create_support_ticket_actions_keyboard(ticket_id, ticket.get('status', 'new'), role='admin')
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
        elif action.startswith('ticket_take_'):
            ticket_id = int(action.split('_')[-1])
            admin_user = User.get_by_max_id(max_user_id, role='admin')
            if admin_user:
                SupportTicket.update_status(ticket_id, 'in_progress', admin_user['id'])
                ticket = SupportTicket.get_ticket_by_id(ticket_id)
                if ticket:
                    from datetime import datetime
                    created_at = ticket.get('created_at')
                    if created_at:
                        try:
                            if isinstance(created_at, str):
                                try:
                                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                except:
                                    created_at = datetime.fromisoformat(created_at.split('+')[0].split('Z')[0])
                            now = datetime.now()
                            if isinstance(created_at, datetime):
                                if created_at.tzinfo:
                                    created_at = created_at.replace(tzinfo=None)
                                diff = now - created_at
                                response_time = int(diff.total_seconds() / 60)
                                if response_time >= 0:
                                    SupportTicket.set_response_time(ticket_id, response_time)
                        except Exception as e:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Ошибка при вычислении времени реакции: {e}")
                
                api.send_message(
                    user_id=max_user_id,
                    text="✅ Обращение взято в работу",
                    attachments=[create_back_keyboard(f"admin_support_ticket_{ticket_id}")]
                )
        elif action.startswith('ticket_resolve_'):
            ticket_id = int(action.split('_')[-1])
            SupportTicket.update_status(ticket_id, 'resolved')
            api.send_message(
                user_id=max_user_id,
                text="✅ Обращение помечено как решенное",
                attachments=[create_back_keyboard(f"admin_support_ticket_{ticket_id}")]
            )
        elif action.startswith('ticket_contact_'):
            ticket_id = int(action.split('_')[-1])
            ticket = SupportTicket.get_ticket_by_id(ticket_id)
            if ticket:
                user_id = ticket.get('user_id')
                target_user = User.get_by_id(user_id)
                if target_user:
                    set_state(max_user_id, 'admin_support_contact', {'ticket_id': ticket_id, 'user_id': user_id})
                    api.send_message(
                        user_id=max_user_id,
                        text=f"💬 Написать пользователю {target_user.get('fio', '')}\n\nОтправьте сообщение:",
                        attachments=[create_cancel_keyboard()]
                    )
        elif action == 'messages':
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
                keyboard = create_back_keyboard("admin_support")
                api.send_message(
                    user_id=max_user_id,
                    text=text,
                    attachments=[keyboard]
                )
                return
            
            text = "💬 Связь с поддержкой:\n\n"
            text += "Вы можете написать сообщение в поддержку.\n"
            text += "Ваше обращение будет зарегистрировано как тикет, и с вами свяжутся в ближайшее время."
            
            buttons = [[
                {"type": "callback", "text": "✉️ Написать в поддержку", "payload": f"admin_write_support_{support_user['id']}"}
            ]]
            buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "admin_support"}])
            keyboard = {
                "type": "inline_keyboard",
                "payload": {"buttons": buttons}
            }
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
        elif action == 'faq':
            faq_list = FAQ.get_faq()
            if not faq_list:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет FAQ",
                    attachments=[create_back_keyboard("admin_support")]
                )
                return
            
            keyboard = create_faq_list_keyboard(faq_list)
            api.send_message(
                user_id=max_user_id,
                text=f"❓ Часто задаваемые вопросы ({len(faq_list)}):",
                attachments=[keyboard]
            )
        elif action.startswith('faq_view_'):
            faq_id = int(action.split('_')[-1])
            faq = FAQ.get_faq_by_id(faq_id)
            if faq:
                text = f"❓ {faq.get('question', '')}\n\n"
                text += f"💬 {faq.get('answer', '')}\n"
                keyboard = create_back_keyboard("admin_support_faq")
                api.send_message(
                    user_id=max_user_id,
                    text=text,
                    attachments=[keyboard]
                )
        elif action == 'faq_add':
            set_state(max_user_id, 'admin_support_faq_add', {})
            api.send_message(
                user_id=max_user_id,
                text="➕ Добавление FAQ\n\nОтправьте данные в формате:\nВопрос\nОтвет\n\nПример:\nКак написать преподавателю?\nВыберите 'Преподаватели' → 'Написать преподавателю'",
                attachments=[create_cancel_keyboard()]
            )
        elif action == 'stats':
            stats = SupportTicket.get_stats()
            text = "📊 Статистика поддержки:\n\n"
            text += f"📋 Всего обращений: {stats.get('total', 0)}\n"
            text += f"🆕 Новых: {stats.get('new', 0)}\n"
            text += f"🔄 В работе: {stats.get('in_progress', 0)}\n"
            text += f"✅ Решено: {stats.get('resolved', 0)}\n"
            text += f"✅ Всего решено: {stats.get('total_resolved', 0)}\n"
            avg_time = stats.get('avg_response_time', 0)
            if avg_time > 0:
                text += f"⏱ Среднее время реакции: {avg_time:.1f} мин."
            else:
                text += f"⏱ Среднее время реакции: не рассчитано"
            
            keyboard = create_back_keyboard("admin_support")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
    
    def start_edit_schedule(self, user: Dict, max_user_id: int, api):
        """Начать редактирование расписания"""
        set_state(max_user_id, 'admin_schedule_edit', {})
        api.send_message(
            user_id=max_user_id,
            text="📅 Редактирование расписания\n\n"
                 "Введите новый URL API для получения расписания.\n"
                 "Формат: http://host:port/endpoint\n\n"
                 "Пример: http://localhost:8001/schedule_1",
            attachments=[create_cancel_keyboard()]
        )

