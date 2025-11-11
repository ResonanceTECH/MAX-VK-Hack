"""Обработчики расписания (общие для студентов и преподавателей)"""
from typing import Dict, Any
from db.models import Group, Teacher
from utils.keyboard import create_schedule_menu_keyboard, create_back_keyboard
import httpx
import os
import logging

logger = logging.getLogger(__name__)

# URL для API расписания
SCHEDULE_API_URL = os.getenv("SCHEDULE_API_URL", "http://schedule:8001/schedule_1")


def get_schedule_from_api(query: str) -> Dict:
    """Получить расписание из API"""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(SCHEDULE_API_URL, params={"query": query})
            # Если 404 - значит расписание не найдено (нет пар)
            if response.status_code == 404:
                return {}
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        # Если 404 - значит расписание не найдено (нет пар)
        if e.response.status_code == 404:
            return {}
        logger.error(f"Ошибка при получении расписания: {e}")
        return {}
    except Exception as e:
        logger.error(f"Ошибка при получении расписания: {e}")
        return {}


def format_teacher_name_for_schedule(fio: str) -> str:
    """Преобразовать ФИО в формат для расписания (Фамилия И. О.)
    
    Входной формат: "Фамилия Имя Отчество" или "Фамилия Имя"
    Выходной формат: "Фамилия И. О." или "Фамилия И."
    """
    if not fio:
        return ""
    
    # Убираем лишние пробелы и разбиваем на части
    parts = [p.strip() for p in fio.strip().split() if p.strip()]
    
    if len(parts) >= 2:
        last_name = parts[0]
        first_name = parts[1]
        middle_name = parts[2] if len(parts) > 2 else None
        
        # Берем первую букву имени (в верхнем регистре)
        first_initial = first_name[0].upper() if first_name else ""
        
        # Берем первую букву отчества (в верхнем регистре), если есть
        if middle_name:
            middle_initial = middle_name[0].upper()
            return f"{last_name} {first_initial}. {middle_initial}."
        else:
            return f"{last_name} {first_initial}."
    elif len(parts) == 1:
        # Если только фамилия, возвращаем как есть
        return parts[0]
    
    return fio

logger = logging.getLogger(__name__)


class ScheduleHandler:
    """Обработчики расписания"""
    
    def show_schedule_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню расписания"""
        keyboard = create_schedule_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="📅 Расписание\n\nВыберите действие:",
            attachments=[keyboard]
        )
    
    def show_schedule_today(self, user: Dict, max_user_id: int, api):
        """Показать расписание на сегодня"""
        from datetime import datetime
        today = datetime.now()
        today_str = today.strftime("%d.%m.%Y")
        weekday = today.strftime("%A")
        weekday_ru = {
            'Monday': 'Понедельник',
            'Tuesday': 'Вторник',
            'Wednesday': 'Среда',
            'Thursday': 'Четверг',
            'Friday': 'Пятница',
            'Saturday': 'Суббота',
            'Sunday': 'Воскресенье'
        }
        weekday_name = weekday_ru.get(weekday, weekday)
        
        # Определяем запрос для расписания
        query = None
        if user['role'] == 'student':
            # Для студентов - получаем группу
            groups = Group.get_user_groups(user['id'])
            if groups:
                query = groups[0]['name']  # Берем первую группу
        elif user['role'] == 'teacher':
            # Для преподавателей - преобразуем ФИО
            query = format_teacher_name_for_schedule(user.get('fio', ''))
        
        if not query:
            text = f"📅 Расписание на сегодня ({weekday_name}, {today_str}):\n\n"
            text += "⚠️ Не удалось определить запрос для расписания.\n"
            text += "Обратитесь к администратору."
            keyboard = create_back_keyboard("menu_schedule")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
            return
        
        # Получаем расписание из API
        schedule_data = get_schedule_from_api(query)
        events_by_calname = schedule_data.get('events_by_calname', {})
        
        text = f"📅 Расписание на сегодня ({weekday_name}, {today_str}):\n\n"
        
        if not events_by_calname:
            text += f"✅ На {weekday_name} занятий нет."
        else:
            # Фильтруем события на сегодня
            today_events = []
            for calname, events in events_by_calname.items():
                for event in events:
                    if event.get('day_of_week') == weekday_name:
                        today_events.append((calname, event))
            
            if not today_events:
                text += f"✅ На {weekday_name} занятий нет.\n"
            else:
                # Группируем по календарям
                events_by_cal = {}
                for calname, event in today_events:
                    if calname not in events_by_cal:
                        events_by_cal[calname] = []
                    events_by_cal[calname].append(event)
                
                for calname, events in events_by_cal.items():
                    text += f"📚 {calname}:\n\n"
                    # Сортируем по времени начала
                    events.sort(key=lambda e: e.get('start', ''))
                    for event in events:
                        text += f"🕐 {event.get('start', '')} - {event.get('end', '')}\n"
                        text += f"📖 {event.get('summary', '')}\n"
                        if event.get('location'):
                            text += f"📍 {event.get('location', '')}\n"
                        if event.get('description'):
                            text += f"👤 {event.get('description', '').strip()}\n"
                        text += f"📆 {event.get('week_parity', '')}\n\n"
        
        keyboard = create_back_keyboard("menu_schedule")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_schedule_week(self, user: Dict, max_user_id: int, api):
        """Показать расписание на неделю"""
        text = "📆 Расписание на неделю\n\n"
        text += "📱 Данный функционал доступен в мини-приложении.\n"
        
        keyboard = create_back_keyboard("menu_schedule")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )

