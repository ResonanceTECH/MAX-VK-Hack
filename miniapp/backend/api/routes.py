"""API routes для мини-приложения"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from db.models import User, Group, Teacher, Message
from miniapp.backend.api.auth import get_current_user

router = APIRouter()

# Pydantic модели для запросов/ответов
class MessageStatusUpdate(BaseModel):
    status: str  # 'unread', 'awaiting', 'replied'

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

@router.get("/user/info")
async def get_user_info(user: Dict = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    all_roles = User.get_all_roles(user['max_user_id'])
    return {
        "id": user['id'],
        "max_user_id": user['max_user_id'],
        "fio": user['fio'],
        "role": user['role'],
        "all_roles": all_roles
    }

@router.get("/groups")
async def get_groups(user: Dict = Depends(get_current_user)):
    """Получить группы пользователя"""
    if user['role'] == 'student':
        groups = Group.get_user_groups(user['id'])
    elif user['role'] == 'teacher':
        groups = Teacher.get_teacher_groups(user['id'])
    else:
        raise HTTPException(status_code=403, detail="Доступ только для студентов и преподавателей")
    
    return groups

@router.get("/groups/{group_id}/students")
async def get_group_students(
    group_id: int,
    user: Dict = Depends(get_current_user)
):
    """Получить студентов группы"""
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail="Доступ только для преподавателей")
    
    # Проверяем, что преподаватель имеет доступ к этой группе
    teacher_groups = Teacher.get_teacher_groups(user['id'])
    if not any(g['id'] == group_id for g in teacher_groups):
        raise HTTPException(status_code=403, detail="Нет доступа к этой группе")
    
    students = Group.get_group_members(group_id)
    return students

@router.get("/messages")
async def get_messages(
    status: Optional[str] = Query(None, description="Фильтр по статусу: unread, awaiting, replied"),
    group_id: Optional[int] = Query(None, description="Фильтр по группе"),
    user: Dict = Depends(get_current_user)
):
    """Получить сообщения для преподавателя"""
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail="Доступ только для преподавателей")
    
    # Получаем сообщения от студентов к этому преподавателю
    messages = Message.get_teacher_messages(user['id'], status=status, group_id=group_id)
    return messages

@router.put("/messages/{message_id}/status")
async def update_message_status(
    message_id: int,
    status_update: MessageStatusUpdate,
    user: Dict = Depends(get_current_user)
):
    """Изменить статус сообщения"""
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail="Доступ только для преподавателей")
    
    if status_update.status not in ['unread', 'awaiting', 'replied']:
        raise HTTPException(status_code=400, detail="Неверный статус")
    
    # Проверяем, что сообщение принадлежит этому преподавателю
    message = Message.get_by_id(message_id)
    if not message or message['to_user_id'] != user['id']:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    
    # Обновляем статус
    Message.update_status(message_id, status_update.status)
    return {"success": True, "message_id": message_id, "status": status_update.status}

@router.get("/messages/stats")
async def get_messages_stats(user: Dict = Depends(get_current_user)):
    """Получить статистику сообщений для преподавателя"""
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail="Доступ только для преподавателей")
    
    stats = Message.get_teacher_stats(user['id'])
    return stats

