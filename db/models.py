"""Модели данных"""
from db.connection import execute_query
from typing import Optional, List, Dict

class User:
    @staticmethod
    def get_by_max_id(max_user_id: int, role: Optional[str] = None) -> Optional[Dict]:
        """Получить пользователя по Max ID. Если указана роль, вернет пользователя с этой ролью"""
        if role:
            query = """
                SELECT id, max_user_id, fio, role, phone, email
                FROM users WHERE max_user_id = %s AND role = %s
            """
            return execute_query(query, (max_user_id, role), fetch_one=True)
        else:
            # Если роль не указана, возвращаем первую найденную запись (приоритет: admin > teacher > student)
            query = """
                SELECT id, max_user_id, fio, role, phone, email
                FROM users WHERE max_user_id = %s
                ORDER BY CASE role 
                    WHEN 'admin' THEN 1 
                    WHEN 'teacher' THEN 2 
                    WHEN 'student' THEN 3 
                    ELSE 4 
                END
                LIMIT 1
            """
            return execute_query(query, (max_user_id,), fetch_one=True)
    
    @staticmethod
    def get_all_roles(max_user_id: int) -> List[Dict]:
        """Получить все роли пользователя"""
        query = """
            SELECT id, max_user_id, fio, role, phone, email
            FROM users WHERE max_user_id = %s
            ORDER BY CASE role 
                WHEN 'admin' THEN 1 
                WHEN 'teacher' THEN 2 
                WHEN 'student' THEN 3 
                ELSE 4 
            END
        """
        return execute_query(query, (max_user_id,), fetch_all=True) or []
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        query = """
            SELECT id, max_user_id, fio, role, phone, email
            FROM users WHERE id = %s
        """
        return execute_query(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def is_verified(max_user_id: int) -> bool:
        """Проверить, верифицирован ли пользователь"""
        return User.get_by_max_id(max_user_id) is not None
    
    @staticmethod
    def get_all_students() -> List[Dict]:
        """Получить всех студентов"""
        query = """
            SELECT id, max_user_id, fio, phone, email
            FROM users
            WHERE role = 'student'
            ORDER BY fio
        """
        return execute_query(query, (), fetch_all=True) or []

class Group:
    @staticmethod
    def get_user_groups(user_id: int) -> List[Dict]:
        """Получить группы пользователя"""
        query = """
            SELECT g.id, g.name, g.semester, g.year, gm.is_headman
            FROM groups g
            JOIN group_members gm ON g.id = gm.group_id
            WHERE gm.user_id = %s
            ORDER BY g.year DESC, g.semester DESC
        """
        return execute_query(query, (user_id,), fetch_all=True) or []
    
    @staticmethod
    def get_group_members(group_id: int) -> List[Dict]:
        """Получить участников группы"""
        query = """
            SELECT u.id, u.max_user_id, u.fio, u.phone, u.email, gm.is_headman
            FROM users u
            JOIN group_members gm ON u.id = gm.user_id
            WHERE gm.group_id = %s AND u.role = 'student'
            ORDER BY u.fio
        """
        return execute_query(query, (group_id,), fetch_all=True) or []
    
    @staticmethod
    def is_headman(user_id: int, group_id: int) -> bool:
        """Проверить, является ли пользователь старостой"""
        query = """
            SELECT is_headman FROM group_members
            WHERE user_id = %s AND group_id = %s
        """
        result = execute_query(query, (user_id, group_id), fetch_one=True)
        return result.get('is_headman', False) if result else False
    
    @staticmethod
    def get_by_id(group_id: int) -> Optional[Dict]:
        """Получить группу по ID"""
        query = """
            SELECT id, name, semester, year
            FROM groups WHERE id = %s
        """
        return execute_query(query, (group_id,), fetch_one=True)
    
    @staticmethod
    def get_all_groups() -> List[Dict]:
        """Получить все группы"""
        query = """
            SELECT id, name, semester, year
            FROM groups
            ORDER BY year DESC, semester DESC, name
        """
        return execute_query(query, (), fetch_all=True) or []

class Teacher:
    @staticmethod
    def get_teacher_groups(teacher_id: int) -> List[Dict]:
        """Получить группы преподавателя"""
        query = """
            SELECT DISTINCT g.id, g.name, g.semester, g.year
            FROM groups g
            JOIN teacher_groups tg ON g.id = tg.group_id
            WHERE tg.teacher_id = %s
            ORDER BY g.year DESC, g.semester DESC, g.name
        """
        return execute_query(query, (teacher_id,), fetch_all=True) or []
    
    @staticmethod
    def get_student_teachers(student_id: int) -> List[Dict]:
        """Получить преподавателей студента (через группы)"""
        query = """
            SELECT DISTINCT u.id, u.max_user_id, u.fio, u.phone, u.email
            FROM users u
            JOIN teacher_groups tg ON u.id = tg.teacher_id
            JOIN group_members gm ON tg.group_id = gm.group_id
            WHERE gm.user_id = %s AND u.role = 'teacher'
            ORDER BY u.fio
        """
        return execute_query(query, (student_id,), fetch_all=True) or []
    
    @staticmethod
    def get_teacher_by_id(teacher_id: int) -> Optional[Dict]:
        """Получить преподавателя по ID"""
        return User.get_by_id(teacher_id)
    
    @staticmethod
    def get_teacher_headmen(teacher_id: int) -> List[Dict]:
        """Получить старост групп преподавателя"""
        query = """
            SELECT DISTINCT u.id, u.max_user_id, u.fio, u.phone, u.email, g.id as group_id, g.name as group_name
            FROM users u
            JOIN group_members gm ON u.id = gm.user_id
            JOIN groups g ON gm.group_id = g.id
            JOIN teacher_groups tg ON g.id = tg.group_id
            WHERE tg.teacher_id = %s AND gm.is_headman = TRUE AND u.role = 'student'
            ORDER BY g.name, u.fio
        """
        return execute_query(query, (teacher_id,), fetch_all=True) or []
    
    @staticmethod
    def get_all_teachers() -> List[Dict]:
        """Получить всех преподавателей"""
        query = """
            SELECT DISTINCT id, max_user_id, fio, phone, email
            FROM users
            WHERE role = 'teacher'
            ORDER BY fio
        """
        return execute_query(query, (), fetch_all=True) or []
    
    @staticmethod
    def create_user(max_user_id: int, fio: str, role: str, phone: Optional[str] = None, email: Optional[str] = None) -> Optional[int]:
        """Создать пользователя"""
        query = """
            INSERT INTO users (max_user_id, fio, role, phone, email)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        result = execute_query(query, (max_user_id, fio, role, phone, email), fetch_one=True)
        return result.get('id') if result else None
    
    @staticmethod
    def update_user(user_id: int, fio: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None) -> bool:
        """Обновить данные пользователя"""
        updates = []
        params = []
        
        if fio is not None:
            updates.append("fio = %s")
            params.append(fio)
        if phone is not None:
            updates.append("phone = %s")
            params.append(phone)
        if email is not None:
            updates.append("email = %s")
            params.append(email)
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"""
            UPDATE users
            SET {', '.join(updates)}
            WHERE id = %s
        """
        execute_query(query, tuple(params))
        return True
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Удалить пользователя"""
        query = """
            DELETE FROM users WHERE id = %s
        """
        execute_query(query, (user_id,))
        return True
    
    @staticmethod
    def assign_user_to_group(user_id: int, group_id: int, is_headman: bool = False) -> bool:
        """Присвоить пользователя группе"""
        query = """
            INSERT INTO group_members (user_id, group_id, is_headman)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, group_id) 
            DO UPDATE SET is_headman = %s
        """
        execute_query(query, (user_id, group_id, is_headman, is_headman))
        return True
    
    @staticmethod
    def remove_user_from_group(user_id: int, group_id: int) -> bool:
        """Удалить пользователя из группы"""
        query = """
            DELETE FROM group_members
            WHERE user_id = %s AND group_id = %s
        """
        execute_query(query, (user_id, group_id))
        return True
    
    @staticmethod
    def assign_teacher_to_group(teacher_id: int, group_id: int, semester: Optional[int] = None, year: Optional[int] = None) -> bool:
        """Привязать преподавателя к группе"""
        query = """
            INSERT INTO teacher_groups (teacher_id, group_id, semester, year)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (teacher_id, group_id, semester, year) DO NOTHING
        """
        execute_query(query, (teacher_id, group_id, semester, year))
        return True

class Message:
    @staticmethod
    def save_message(from_user_id: int, to_user_id: int, text: str, 
                    max_message_id: str, group_id: Optional[int] = None):
        """Сохранить сообщение в БД"""
        query = """
            INSERT INTO messages (from_user_id, to_user_id, group_id, text, max_message_id, status)
            VALUES (%s, %s, %s, %s, %s, 'unread')
        """
        return execute_query(query, (from_user_id, to_user_id, group_id, text, max_message_id))
    
    @staticmethod
    def get_teacher_messages(teacher_id: int, status: Optional[str] = None, 
                            group_id: Optional[int] = None) -> List[Dict]:
        """Получить сообщения для преподавателя от студентов"""
        conditions = ["to_user_id = %s"]
        params = [teacher_id]
        
        if status:
            conditions.append("status = %s")
            params.append(status)
        
        if group_id:
            conditions.append("group_id = %s")
            params.append(group_id)
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT 
                m.id,
                m.from_user_id,
                u1.fio as from_user_fio,
                m.to_user_id,
                u2.fio as to_user_fio,
                m.group_id,
                g.name as group_name,
                m.text,
                m.status,
                m.created_at
            FROM messages m
            JOIN users u1 ON m.from_user_id = u1.id
            JOIN users u2 ON m.to_user_id = u2.id
            LEFT JOIN groups g ON m.group_id = g.id
            WHERE {where_clause}
            ORDER BY m.created_at DESC
        """
        return execute_query(query, tuple(params), fetch_all=True) or []
    
    @staticmethod
    def get_by_id(message_id: int) -> Optional[Dict]:
        """Получить сообщение по ID"""
        query = """
            SELECT id, from_user_id, to_user_id, group_id, text, status, created_at
            FROM messages WHERE id = %s
        """
        return execute_query(query, (message_id,), fetch_one=True)
    
    @staticmethod
    def update_status(message_id: int, status: str):
        """Обновить статус сообщения"""
        query = """
            UPDATE messages SET status = %s WHERE id = %s
        """
        return execute_query(query, (status, message_id))
    
    @staticmethod
    def get_teacher_stats(teacher_id: int) -> Dict:
        """Получить статистику сообщений для преподавателя"""
        query = """
            SELECT 
                status,
                COUNT(*) as count
            FROM messages
            WHERE to_user_id = %s
            GROUP BY status
        """
        results = execute_query(query, (teacher_id,), fetch_all=True) or []
        
        stats = {
            'unread': 0,
            'awaiting': 0,
            'replied': 0,
            'total': 0
        }
        
        for row in results:
            status = row.get('status', 'unread')
            count = row.get('count', 0)
            stats[status] = count
            stats['total'] += count
        
        return stats

