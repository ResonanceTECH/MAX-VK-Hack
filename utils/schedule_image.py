"""Генерация изображения расписания"""
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Optional
from datetime import datetime
import io
import os


def generate_schedule_image(events_by_calname: Dict, group_name: Optional[str] = None) -> io.BytesIO:
    """Генерирует изображение расписания на неделю"""
    weekdays_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    pair_times = [
        ("1", "09:00", "10:30"),
        ("2", "10:40", "12:10"),
        ("3", "12:40", "14:10"),
        ("4", "14:20", "15:50"),
        ("5", "16:20", "17:50"),
        ("6", "18:00", "19:30"),
    ]
    
    # Параметры изображения
    cell_width = 200
    cell_height = 80
    header_height = 100
    pair_col_width = 60
    day_col_width = cell_width
    margin = 20
    
    num_days = len(weekdays_order)
    num_pairs = len(pair_times)
    
    # Размеры изображения
    img_width = margin * 2 + pair_col_width + (day_col_width * num_days)
    img_height = margin * 2 + header_height + (cell_height * num_pairs)
    
    # Создаем изображение
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Пытаемся загрузить шрифты
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        header_font = ImageFont.truetype("arial.ttf", 14)
        text_font = ImageFont.truetype("arial.ttf", 10)
        small_font = ImageFont.truetype("arial.ttf", 8)
    except:
        # Если шрифты не найдены, используем стандартные
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Заголовок
    title = f"Расписание группы {group_name}" if group_name else "Расписание"
    draw.text((margin, margin), title, fill='black', font=title_font)
    
    # Дата обновления
    update_text = f"Последнее обновление {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    draw.text((margin, margin + 30), update_text, fill='gray', font=small_font)
    
    # Легенда времени пар (справа вверху)
    legend_x = img_width - margin - 150
    legend_y = margin
    draw.text((legend_x, legend_y), "Время пар:", fill='black', font=header_font)
    for i, (num, start, end) in enumerate(pair_times):
        y = legend_y + 20 + (i * 15)
        draw.text((legend_x, y), f"{num} пара: {start}–{end}", fill='black', font=small_font)
    
    # Начало таблицы
    table_start_x = margin
    table_start_y = margin + header_height
    
    # Рисуем заголовки дней
    for i, day in enumerate(weekdays_order):
        x = table_start_x + pair_col_width + (i * day_col_width)
        y = table_start_y
        # Фон заголовка
        draw.rectangle([x, y, x + day_col_width - 1, y + 30], fill='#4A90E2', outline='black')
        draw.text((x + 5, y + 5), day, fill='white', font=header_font)
    
    # Рисуем номера пар и время
    for i, (pair_num, start, end) in enumerate(pair_times):
        y = table_start_y + 30 + (i * cell_height)
        # Номер пары
        draw.rectangle([table_start_x, y, table_start_x + pair_col_width - 1, y + cell_height - 1], 
                      fill='#E8F4F8', outline='black')
        draw.text((table_start_x + 5, y + 5), f"{pair_num} пара", fill='black', font=header_font)
        draw.text((table_start_x + 5, y + 20), f"{start}-{end}", fill='gray', font=small_font)
    
    # Группируем события по дням и парам
    events_by_day_pair = {}
    for calname, events in events_by_calname.items():
        for event in events:
            day = event.get('day_of_week', '')
            start_time = event.get('start', '')
            
            # Определяем номер пары по времени начала
            pair_num = None
            for idx, (num, start, end) in enumerate(pair_times):
                if start_time == start:
                    pair_num = idx
                    break
            
            if pair_num is not None and day in weekdays_order:
                key = (day, pair_num)
                if key not in events_by_day_pair:
                    events_by_day_pair[key] = []
                events_by_day_pair[key].append(event)
    
    # Рисуем события
    for (day, pair_num), events in events_by_day_pair.items():
        day_idx = weekdays_order.index(day)
        x = table_start_x + pair_col_width + (day_idx * day_col_width)
        y = table_start_y + 30 + (pair_num * cell_height)
        
        # Фон ячейки
        draw.rectangle([x, y, x + day_col_width - 1, y + cell_height - 1], 
                      fill='white', outline='black')
        
        # Рисуем события (максимум 2, если их больше - обрезаем)
        events_to_show = events[:2]
        for i, event in enumerate(events_to_show):
            event_y = y + 5 + (i * 35)
            
            # Название предмета
            summary = event.get('summary', '')[:30]  # Обрезаем длинные названия
            draw.text((x + 2, event_y), summary, fill='black', font=text_font)
            
            # Тип занятия и преподаватель
            desc = event.get('description', '').strip()[:25]
            if desc:
                draw.text((x + 2, event_y + 12), desc, fill='gray', font=small_font)
            
            # Место
            location = event.get('location', '')[:20]
            if location:
                draw.text((x + 2, event_y + 22), location, fill='blue', font=small_font)
    
    # Сохраняем в BytesIO
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

