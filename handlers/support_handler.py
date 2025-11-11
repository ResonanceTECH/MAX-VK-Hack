"""Обработчики для поддержки"""
from typing import Dict, Any
from db.models import User, SupportTicket
from db.connection import execute_query
from utils.keyboard import (
    create_support_tickets_status_keyboard, create_support_tickets_list_keyboard,
    create_support_ticket_actions_keyboard,
    create_back_keyboard, create_cancel_keyboard
)
from utils.states import set_state
import logging

logger = logging.getLogger(__name__)


class SupportHandler:
    """Обработчики для поддержки"""
    
    def handle_support_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия поддержки (для роли support)"""
        action = payload.replace('support_', '')
        
        if action == 'tickets':
            keyboard = create_support_tickets_status_keyboard(role='support')
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
                    attachments=[create_support_tickets_status_keyboard(role='support')]
                )
                return
            
            keyboard = create_support_tickets_list_keyboard(tickets, prefix="support_ticket", back_payload="support_tickets")
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
                    attachments=[create_support_tickets_status_keyboard(role='support')]
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
            
            keyboard = create_support_ticket_actions_keyboard(ticket_id, ticket.get('status', 'new'), role='support')
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
        elif action.startswith('ticket_take_'):
            ticket_id = int(action.split('_')[-1])
            support_user = User.get_by_max_id(max_user_id, role='support')
            if support_user:
                SupportTicket.update_status(ticket_id, 'in_progress', support_user['id'])
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
                            logger.error(f"Ошибка при вычислении времени реакции: {e}")
                
                api.send_message(
                    user_id=max_user_id,
                    text="✅ Обращение взято в работу",
                    attachments=[create_back_keyboard(f"support_ticket_{ticket_id}")]
                )
        elif action.startswith('ticket_resolve_'):
            ticket_id = int(action.split('_')[-1])
            SupportTicket.update_status(ticket_id, 'resolved')
            api.send_message(
                user_id=max_user_id,
                text="✅ Обращение помечено как решенное",
                attachments=[create_back_keyboard(f"support_ticket_{ticket_id}")]
            )
        elif action.startswith('ticket_contact_'):
            ticket_id = int(action.split('_')[-1])
            ticket = SupportTicket.get_ticket_by_id(ticket_id)
            if ticket:
                user_id = ticket.get('user_id')
                target_user = User.get_by_id(user_id)
                if target_user:
                    set_state(max_user_id, 'waiting_message_from_support', {'ticket_id': ticket_id, 'user_id': user_id})
                    api.send_message(
                        user_id=max_user_id,
                        text=f"💬 Написать пользователю {target_user.get('fio', '')}\n\nОтправьте сообщение:",
                        attachments=[create_cancel_keyboard()]
                    )
        elif action == 'messages':
            users_query = """
                SELECT DISTINCT u.id, u.max_user_id, u.first_name, u.last_name, u.middle_name, u.role,
                       TRIM(CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name)) as fio,
                       COUNT(st.id) as tickets_count,
                       MAX(st.created_at) as last_ticket_date
                FROM support_tickets st
                JOIN users u ON st.user_id = u.id
                GROUP BY u.id, u.max_user_id, u.first_name, u.last_name, u.middle_name, u.role
                ORDER BY last_ticket_date DESC
                LIMIT 50
            """
            users = execute_query(users_query, (), fetch_all=True) or []
            
            if not users:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет пользователей, которые писали в поддержку",
                    attachments=[create_back_keyboard("main_menu")]
                )
                return
            
            buttons = []
            for user_data in users:
                user_id = user_data['id']
                fio = user_data.get('fio', 'Неизвестно')
                tickets_count = user_data.get('tickets_count', 0)
                buttons.append([{
                    "type": "callback",
                    "text": f"👤 {fio} ({tickets_count} обращений)",
                    "payload": f"support_message_user_{user_id}"
                }])
            
            buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}])
            keyboard = {
                "type": "inline_keyboard",
                "payload": {"buttons": buttons}
            }
            
            api.send_message(
                user_id=max_user_id,
                text=f"💬 Пользователи, которые писали в поддержку ({len(users)}):\n\nВыберите пользователя для отправки сообщения:",
                attachments=[keyboard]
            )
        elif action.startswith('message_user_'):
            user_id = int(action.split('_')[-1])
            target_user = User.get_by_id(user_id)
            if not target_user:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Пользователь не найден",
                    attachments=[create_back_keyboard("support_messages")]
                )
                return
            
            set_state(max_user_id, 'waiting_message_from_support', {'user_id': user_id})
            api.send_message(
                user_id=max_user_id,
                text=f"💬 Написать пользователю {target_user.get('fio', '')}\n\nОтправьте сообщение:",
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
            
            keyboard = create_back_keyboard("main_menu")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )

