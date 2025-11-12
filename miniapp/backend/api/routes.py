"""API routes для мини-приложения"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from db.models import User, Group, Teacher, Message, SupportTicket, News
from db.connection import execute_query
from api.auth import get_current_user

router = APIRouter()


# Pydantic модели для запросов/ответов
class MessageStatusUpdate(BaseModel):
    status: str  # 'unread', 'read'


class MessageResponse(BaseModel):
    id: int
    from_user_id: int
    from_user_fio: str
    to_user_id: int
    to_user_fio: str
    group_id: Optional[int]
    group_name: Optional[str]
    text: str
    status: Optional[str]
    created_at: str


class GroupResponse(BaseModel):
    id: int
    name: str
    semester: Optional[int]
    year: Optional[int]


class StudentResponse(BaseModel):
    id: int
    fio: str
    max_user_id: Optional[int]
    is_headman: bool


@router.get("/user/info", tags=["User"])
async def get_user_info(user: Dict = Depends(get_current_user)):
    """
    Получить информацию о текущем пользователе
    
    Возвращает информацию о текущем пользователе, включая все доступные роли.
    """
    all_roles = User.get_all_roles(user['max_user_id'])
    return {
        "id": user['id'],
        "max_user_id": user['max_user_id'],
        "fio": user['fio'],
        "role": user['role'],
        "all_roles": all_roles
    }


@router.get("/groups", tags=["Groups"])
async def get_groups(user: Dict = Depends(get_current_user)):
    """
    Получить группы пользователя
    
    Для студентов возвращает группы, в которых они состоят.
    Для преподавателей возвращает группы, которые они ведут.
    """
    if user['role'] == 'student':
        groups = Group.get_user_groups(user['id'])
    elif user['role'] == 'teacher':
        groups = Teacher.get_teacher_groups(user['id'])
    else:
        raise HTTPException(status_code=403, detail="Доступ только для студентов и преподавателей")

    return groups


@router.get("/groups/{group_id}/students", tags=["Groups"])
async def get_group_students(
        group_id: int,
        user: Dict = Depends(get_current_user)
):
    """
    Получить список студентов группы
    
    - **group_id**: ID группы
    - Доступно для студентов (только своей группы), преподавателей (только своих групп) и администрации (все группы)
    """
    # Для студентов - проверяем, что они в этой группе
    if user['role'] == 'student':
        user_groups = Group.get_user_groups(user['id'])
        if not any(g['id'] == group_id for g in user_groups):
            raise HTTPException(status_code=403, detail="Нет доступа к этой группе")
    # Для преподавателей - проверяем, что они ведут эту группу
    elif user['role'] == 'teacher':
        teacher_groups = Teacher.get_teacher_groups(user['id'])
        if not any(g['id'] == group_id for g in teacher_groups):
            raise HTTPException(status_code=403, detail="Нет доступа к этой группе")
    # Для админов - доступ ко всем группам
    elif user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для студентов, преподавателей и администрации")

    students = Group.get_group_members(group_id)
    return students


@router.get("/messages", tags=["Messages"])
async def get_messages(
        status: Optional[str] = Query(None, description="Фильтр по статусу: unread, read"),
        group_id: Optional[int] = Query(None, description="Фильтр по группе"),
        user: Dict = Depends(get_current_user)
):
    """
    Получить сообщения для пользователя
    
    Возвращает все сообщения, отправленные текущему пользователю.
    Поддерживает фильтрацию по статусу и группе.
    """
    # Для всех ролей получаем все сообщения, которые были отправлены этому пользователю
    # (от студентов, преподавателей, поддержки, администрации - от всех)
    messages = Message.get_user_messages(user['id'], status=status, group_id=group_id)
    return messages


@router.put("/messages/{message_id}/status", tags=["Messages"])
async def update_message_status(
        message_id: int,
        status_update: MessageStatusUpdate,
        user: Dict = Depends(get_current_user)
):
    """
    Изменить статус сообщения
    
    - **message_id**: ID сообщения
    - **status**: Новый статус (unread или read)
    """
    # Доступно для всех ролей
    if status_update.status not in ['unread', 'read']:
        raise HTTPException(status_code=400, detail="Неверный статус. Допустимые значения: unread, read")

    # Проверяем, что сообщение принадлежит этому преподавателю
    message = Message.get_by_id(message_id)
    if not message or message['to_user_id'] != user['id']:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")

    # Обновляем статус
    Message.update_status(message_id, status_update.status)
    return {"success": True, "message_id": message_id, "status": status_update.status}


@router.get("/messages/stats", tags=["Messages"])
async def get_messages_stats(user: Dict = Depends(get_current_user)):
    """
    Получить статистику сообщений для пользователя
    
    Возвращает количество непрочитанных и прочитанных сообщений.
    """
    # Статистика доступна для всех ролей
    stats = Message.get_teacher_stats(user['id'])  # Метод работает для любого user_id
    return stats


# ========== Endpoints для студентов ==========

@router.get("/teachers", tags=["Teachers"])
async def get_student_teachers(user: Dict = Depends(get_current_user)):
    """
    Получить список преподавателей
    
    Для студентов возвращает преподавателей их групп.
    Для преподавателей возвращает всех преподавателей (кроме себя).
    """
    if user['role'] == 'student':
        teachers = Teacher.get_student_teachers(user['id'])
        return teachers
    elif user['role'] == 'teacher':
        # Для преподавателей возвращаем всех преподавателей (исключая себя)
        all_teachers = Teacher.get_all_teachers()
        teachers = [t for t in all_teachers if t['id'] != user['id']]
        return teachers
    else:
        raise HTTPException(status_code=403, detail="Доступ только для студентов и преподавателей")


@router.get("/news", tags=["News"])
async def get_news(user: Dict = Depends(get_current_user)):
    """
    Получить новости для пользователя
    
    Возвращает новости в зависимости от роли пользователя и его групп.
    """
    from db.models import News
    news = News.get_news_by_role(user['role'], user['id'], limit=50)
    return news


# ========== Endpoints для поддержки ==========

@router.get("/support/tickets", tags=["Support"])
async def get_support_tickets(
        status: Optional[str] = Query(None, description="Фильтр по статусу: new, in_progress, resolved"),
        user: Dict = Depends(get_current_user)
):
    """
    Получить обращения в поддержку
    
    Доступно только для роли support.
    Поддерживает фильтрацию по статусу.
    """
    if user['role'] != 'support':
        raise HTTPException(status_code=403, detail="Доступ только для поддержки")

    tickets = SupportTicket.get_tickets(status=status)
    # get_tickets возвращает fio, переименуем в user_fio для единообразия
    for ticket in tickets:
        if 'fio' in ticket:
            ticket['user_fio'] = ticket['fio']
    return tickets


@router.put("/support/tickets/{ticket_id}/status", tags=["Support"])
async def update_ticket_status(
        ticket_id: int,
        status_update: Dict,
        user: Dict = Depends(get_current_user)
):
    """
    Изменить статус обращения в поддержку
    
    - **ticket_id**: ID обращения
    - **status**: Новый статус (new, in_progress, resolved)
    """
    if user['role'] != 'support':
        raise HTTPException(status_code=403, detail="Доступ только для поддержки")

    new_status = status_update.get('status')
    if new_status not in ['new', 'in_progress', 'resolved']:
        raise HTTPException(status_code=400, detail="Неверный статус")

    SupportTicket.update_status(ticket_id, new_status, user['id'])
    return {"success": True}


@router.get("/support/stats", tags=["Support"])
async def get_support_stats(user: Dict = Depends(get_current_user)):
    """
    Получить статистику поддержки
    
    Возвращает статистику по обращениям в поддержку.
    """
    if user['role'] != 'support':
        raise HTTPException(status_code=403, detail="Доступ только для поддержки")

    stats = SupportTicket.get_stats()
    return stats


# ========== Endpoints для администрации ==========

@router.get("/admin/students", tags=["Admin - Students"])
async def get_all_students(user: Dict = Depends(get_current_user)):
    """
    Получить всех студентов
    
    Доступно только для роли admin.
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    students = User.get_all_students()
    return students


@router.post("/admin/students", tags=["Admin - Students"])
async def create_student(student_data: Dict, user: Dict = Depends(get_current_user)):
    """
    Создать нового студента
    
    Обязательные поля:
    - **max_user_id**: ID пользователя в Max
    - **fio**: ФИО студента
    
    Опциональные поля:
    - **phone**: Телефон
    - **email**: Email
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    student_id = Teacher.create_user(
        max_user_id=student_data['max_user_id'],
        fio=student_data['fio'],
        role='student',
        phone=student_data.get('phone'),
        email=student_data.get('email')
    )
    return {"id": student_id, "success": True}


@router.put("/admin/students/{student_id}", tags=["Admin - Students"])
async def update_student(
        student_id: int,
        student_data: Dict,
        user: Dict = Depends(get_current_user)
):
    """
    Обновить данные студента
    
    - **student_id**: ID студента
    - Можно обновить: fio, phone, email
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    Teacher.update_user(
        student_id,
        student_data.get('fio'),
        student_data.get('phone'),
        student_data.get('email')
    )
    return {"success": True}


@router.delete("/admin/students/{student_id}", tags=["Admin - Students"])
async def delete_student(student_id: int, user: Dict = Depends(get_current_user)):
    """
    Удалить студента
    
    - **student_id**: ID студента
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    Teacher.delete_user(student_id)
    return {"success": True}


@router.get("/admin/teachers", tags=["Admin - Teachers"])
async def get_all_teachers(user: Dict = Depends(get_current_user)):
    """
    Получить всех преподавателей
    
    Доступно только для роли admin.
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    teachers = Teacher.get_all_teachers()
    return teachers


@router.post("/admin/teachers", tags=["Admin - Teachers"])
async def create_teacher(teacher_data: Dict, user: Dict = Depends(get_current_user)):
    """
    Создать нового преподавателя
    
    Обязательные поля:
    - **max_user_id**: ID пользователя в Max
    - **fio**: ФИО преподавателя
    
    Опциональные поля:
    - **phone**: Телефон
    - **email**: Email
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    teacher_id = Teacher.create_user(
        max_user_id=teacher_data['max_user_id'],
        fio=teacher_data['fio'],
        role='teacher',
        phone=teacher_data.get('phone'),
        email=teacher_data.get('email')
    )
    return {"id": teacher_id, "success": True}


@router.put("/admin/teachers/{teacher_id}", tags=["Admin - Teachers"])
async def update_teacher(
        teacher_id: int,
        teacher_data: Dict,
        user: Dict = Depends(get_current_user)
):
    """
    Обновить данные преподавателя
    
    - **teacher_id**: ID преподавателя
    - Можно обновить: fio, phone, email
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    Teacher.update_user(
        teacher_id,
        teacher_data.get('fio'),
        teacher_data.get('phone'),
        teacher_data.get('email')
    )
    return {"success": True}


@router.delete("/admin/teachers/{teacher_id}", tags=["Admin - Teachers"])
async def delete_teacher(teacher_id: int, user: Dict = Depends(get_current_user)):
    """
    Удалить преподавателя
    
    - **teacher_id**: ID преподавателя
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    Teacher.delete_user(teacher_id)
    return {"success": True}


@router.get("/admin/groups", tags=["Admin - Groups"])
async def get_all_groups(user: Dict = Depends(get_current_user)):
    """
    Получить все группы
    
    Доступно только для роли admin.
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    groups = Group.get_all_groups()
    return groups


@router.post("/admin/groups", tags=["Admin - Groups"])
async def create_group(
        group_data: dict,
        user: Dict = Depends(get_current_user)
):
    """
    Создать новую группу
    
    Обязательные поля:
    - **name**: Название группы
    
    Опциональные поля:
    - **semester**: Семестр
    - **year**: Год
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    name = group_data.get('name')
    if not name:
        raise HTTPException(status_code=400, detail="Название группы обязательно")

    semester = group_data.get('semester')
    year = group_data.get('year')

    group_id = Group.create_group(name, semester, year)
    if not group_id:
        raise HTTPException(status_code=500, detail="Ошибка при создании группы")

    return {"success": True, "id": group_id}


@router.put("/admin/groups/{group_id}", tags=["Admin - Groups"])
async def update_group(
        group_id: int,
        group_data: dict,
        user: Dict = Depends(get_current_user)
):
    """
    Обновить группу
    
    - **group_id**: ID группы
    - Можно обновить: name, semester, year
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    # Проверяем, что группа существует
    group = Group.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    name = group_data.get('name')
    semester = group_data.get('semester')
    year = group_data.get('year')

    success = Group.update_group(group_id, name, semester, year)
    if not success:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")

    return {"success": True}


@router.delete("/admin/groups/{group_id}", tags=["Admin - Groups"])
async def delete_group(
        group_id: int,
        user: Dict = Depends(get_current_user)
):
    """
    Удалить группу
    
    - **group_id**: ID группы
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    # Проверяем, что группа существует
    group = Group.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    Group.delete_group(group_id)
    return {"success": True}


@router.post("/admin/groups/{group_id}/students/{student_id}", tags=["Admin - Groups"])
async def add_student_to_group(
        group_id: int,
        student_id: int,
        user: Dict = Depends(get_current_user)
):
    """
    Добавить студента в группу
    
    - **group_id**: ID группы
    - **student_id**: ID студента
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    Teacher.assign_user_to_group(student_id, group_id)
    return {"success": True}


@router.delete("/admin/groups/{group_id}/students/{student_id}", tags=["Admin - Groups"])
async def remove_student_from_group(
        group_id: int,
        student_id: int,
        user: Dict = Depends(get_current_user)
):
    """
    Удалить студента из группы
    
    - **group_id**: ID группы
    - **student_id**: ID студента
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    query = "DELETE FROM group_members WHERE user_id = %s AND group_id = %s"
    execute_query(query, (student_id, group_id))
    return {"success": True}


@router.put("/admin/groups/{group_id}/headman/{student_id}", tags=["Admin - Groups"])
async def set_headman(
        group_id: int,
        student_id: int,
        user: Dict = Depends(get_current_user)
):
    """
    Назначить старосту группы
    
    - **group_id**: ID группы
    - **student_id**: ID студента, который станет старостой
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    # Сначала снимаем старосту со всех студентов группы
    query1 = "UPDATE group_members SET is_headman = FALSE WHERE group_id = %s"
    execute_query(query1, (group_id,))

    # Назначаем нового старосту
    query2 = "UPDATE group_members SET is_headman = TRUE WHERE user_id = %s AND group_id = %s"
    execute_query(query2, (student_id, group_id))
    return {"success": True}


@router.post("/admin/news", tags=["Admin - News"])
async def create_news(news_data: Dict, user: Dict = Depends(get_current_user)):
    """
    Создать новость
    
    Обязательные поля:
    - **title**: Заголовок новости
    - **description**: Описание новости
    
    Опциональные поля:
    - **hashtags**: Хэштеги через запятую
    - **target_role**: Целевая роль (student, teacher, all или null для всех)
    - **target_group_id**: ID целевой группы (null для всех групп)
    """
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Доступ только для администрации")

    query = """
        INSERT INTO news (title, description, hashtags, target_role, target_group_id, created_by)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    result = execute_query(
        query,
        (
            news_data['title'],
            news_data['description'],
            news_data.get('hashtags'),
            news_data.get('target_role'),
            news_data.get('target_group_id'),
            user['id']
        ),
        fetch_one=True
    )
    return {"id": result['id'], "success": True} if result else {"success": False}
