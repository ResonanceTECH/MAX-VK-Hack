from datetime import datetime, timedelta

DAYS_OF_WEEK = {
    0: "Понедельник", 1: "Вторник", 2: "Среда",
    3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"
}


def format_time(dt):
    return dt.strftime("%H:%M")


def get_week_parity(dt):
    """
    Определяет четность недели на основе номера недели от начала учебного года (1 сентября).
    Учебный год начинается 1 сентября. Неделя считается от понедельника.
    """
    # Работаем только с датой, без учета времени и timezone
    if hasattr(dt, 'date'):
        date_only = dt.date()
    else:
        date_only = dt
    
    # Определяем начало учебного года (1 сентября текущего или прошлого года)
    if date_only.month >= 9:  # Сентябрь-декабрь - текущий учебный год
        academic_year_start = datetime(date_only.year, 9, 1).date()
    else:  # Январь-август - учебный год начался в прошлом году
        academic_year_start = datetime(date_only.year - 1, 9, 1).date()
    
    # Находим первый понедельник учебного года
    # weekday() возвращает 0 для понедельника, 6 для воскресенья
    # Если 1 сентября - понедельник, то days_until_monday = 0
    # Иначе находим следующий понедельник
    days_until_monday = (7 - academic_year_start.weekday()) % 7
    first_monday = academic_year_start + timedelta(days=days_until_monday)
    
    # Вычисляем разницу в днях
    days_diff = (date_only - first_monday).days
    
    # Если дата раньше первого понедельника, считаем от предыдущего учебного года
    if days_diff < 0:
        academic_year_start = datetime(academic_year_start.year - 1, 9, 1).date()
        days_until_monday = (7 - academic_year_start.weekday()) % 7
        first_monday = academic_year_start + timedelta(days=days_until_monday)
        days_diff = (date_only - first_monday).days
    
    # Вычисляем номер недели (начиная с 0)
    week_number = days_diff // 7
    
    # Определяем четность (неделя 0 = нечетная, неделя 1 = четная и т.д.)
    return "нечетная" if week_number % 2 == 0 else "четная"
