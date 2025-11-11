"""Модели данных"""
from db.connection import execute_query
from typing import Optional, List, Dict


def format_fio(first_name: str, last_name: str, middle_name: Optional[str] = None) -> str:
    """Формирует полное ФИО из отдельных полей"""
    parts = [last_name, first_name]
    if middle_name:
        parts.append(middle_name)
    return ' '.join(parts)

class User:
    @staticmethod
    def get_by_max_id(max_user_id: int, role: Optional[str] = None) -> Optional[Dict]:
        """Получить пользователя по Max ID. Если указана роль, вернет пользователя с этой ролью"""
        if role:
            query = """
                SELECT id, max_user_id, first_name, last_name, middle_name, role, phone, email,
                       TRIM(CONCAT_WS(' ', last_name, first_name, middle_name)) as fio
                FROM users WHERE max_user_id = %s AND role = %s
            """
            return execute_query(query, (max_user_id, role), fetch_one=True)
        else:
            # Если роль не указана, возвращаем первую найденную запись (приоритет: admin > support > teacher > student)
            query = """
                SELECT id, max_user_id, first_name, last_name, middle_name, role, phone, email,
                       TRIM(CONCAT_WS(' ', last_name, first_name, middle_name)) as fio
                FROM users WHERE max_user_id = %s
                ORDER BY CASE role 
                    WHEN 'admin' THEN 1 
                    WHEN 'support' THEN 2 
                    WHEN 'teacher' THEN 3 
                    WHEN 'student' THEN 4 
                    ELSE 5 
                END
                LIMIT 1
            """
            return execute_query(query, (max_user_id,), fetch_one=True)
    
    @staticmethod
    def get_all_roles(max_user_id: int) -> List[Dict]:
        """Получить все роли пользователя"""
        query = """
            SELECT id, max_user_id, first_name, last_name, middle_name, role, phone, email,
                   TRIM(CONCAT_WS(' ', last_name, first_name, middle_name)) as fio
            FROM users WHERE max_user_id = %s
            ORDER BY CASE role 
                WHEN 'admin' THEN 1 
                WHEN 'support' THEN 2 
                WHEN 'teacher' THEN 3 
                WHEN 'student' THEN 4 
                ELSE 5 
            END
        """
        return execute_query(query, (max_user_id,), fetch_all=True) or []
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        query = """
            SELECT id, max_user_id, first_name, last_name, middle_name, role, phone, email,
                   TRIM(CONCAT_WS(' ', last_name, first_name, middle_name)) as fio
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
            SELECT id, max_user_id, first_name, last_name, middle_name, phone, email,
                   TRIM(CONCAT_WS(' ', last_name, first_name, middle_name)) as fio
            FROM users
            WHERE role = 'student'
            ORDER BY last_name, first_name, middle_name
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
            SELECT u.id, u.max_user_id, u.first_name, u.last_name, u.middle_name, u.phone, u.email, gm.is_headman,
                   TRIM(CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name)) as fio
            FROM users u
            JOIN group_members gm ON u.id = gm.user_id
            WHERE gm.group_id = %s AND u.role = 'student'
            ORDER BY u.last_name, u.first_name, u.middle_name
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
    
    @staticmethod
    def create_group(name: str, semester: Optional[int] = None, year: Optional[int] = None) -> Optional[int]:
        """Создать новую группу"""
        query = """
            INSERT INTO groups (name, semester, year)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        result = execute_query(query, (name, semester, year), fetch_one=True)
        return result.get('id') if result else None
    
    @staticmethod
    def update_group(group_id: int, name: Optional[str] = None, semester: Optional[int] = None, year: Optional[int] = None) -> bool:
        """Обновить группу"""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if semester is not None:
            updates.append("semester = %s")
            params.append(semester)
        if year is not None:
            updates.append("year = %s")
            params.append(year)
        
        if not updates:
            return False
        
        params.append(group_id)
        query = f"UPDATE groups SET {', '.join(updates)} WHERE id = %s"
        execute_query(query, tuple(params))
        return True
    
    @staticmethod
    def delete_group(group_id: int) -> bool:
        """Удалить группу"""
        # Каскадное удаление через ON DELETE CASCADE в схеме БД
        query = "DELETE FROM groups WHERE id = %s"
        execute_query(query, (group_id,))
        return True

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
            SELECT DISTINCT u.id, u.max_user_id, u.first_name, u.last_name, u.middle_name, u.phone, u.email,
                   TRIM(CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name)) as fio
            FROM users u
            JOIN teacher_groups tg ON u.id = tg.teacher_id
            JOIN group_members gm ON tg.group_id = gm.group_id
            WHERE gm.user_id = %s AND u.role = 'teacher'
            ORDER BY u.last_name, u.first_name, u.middle_name
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
            SELECT DISTINCT u.id, u.max_user_id, u.first_name, u.last_name, u.middle_name, u.phone, u.email, g.id as group_id, g.name as group_name,
                   TRIM(CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name)) as fio
            FROM users u
            JOIN group_members gm ON u.id = gm.user_id
            JOIN groups g ON gm.group_id = g.id
            JOIN teacher_groups tg ON g.id = tg.group_id
            WHERE tg.teacher_id = %s AND gm.is_headman = TRUE AND u.role = 'student'
            ORDER BY g.name, u.last_name, u.first_name, u.middle_name
        """
        return execute_query(query, (teacher_id,), fetch_all=True) or []
    
    @staticmethod
    def get_all_teachers() -> List[Dict]:
        """Получить всех преподавателей"""
        query = """
            SELECT DISTINCT id, max_user_id, first_name, last_name, middle_name, phone, email,
                   TRIM(CONCAT_WS(' ', last_name, first_name, middle_name)) as fio
            FROM users
            WHERE role = 'teacher'
            ORDER BY last_name, first_name, middle_name
        """
        return execute_query(query, (), fetch_all=True) or []
    
    @staticmethod
    def create_user(max_user_id: int, fio: str, role: str, phone: Optional[str] = None, email: Optional[str] = None) -> Optional[int]:
        """Создать пользователя. fio должен быть в формате "Фамилия Имя Отчество" или "Фамилия Имя" """
        # Парсим ФИО на части
        parts = fio.strip().split()
        if len(parts) >= 2:
            last_name = parts[0]
            first_name = parts[1]
            middle_name = parts[2] if len(parts) > 2 else None
        else:
            # Если формат неправильный, используем как есть
            last_name = fio
            first_name = ""
            middle_name = None
        
        query = """
            INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = execute_query(query, (max_user_id, first_name, last_name, middle_name, role, phone, email), fetch_one=True)
        return result.get('id') if result else None
    
    @staticmethod
    def update_user(user_id: int, fio: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None) -> bool:
        """Обновить данные пользователя. fio должен быть в формате "Фамилия Имя Отчество" или "Фамилия Имя" """
        updates = []
        params = []
        
        if fio is not None:
            # Парсим ФИО на части
            parts = fio.strip().split()
            if len(parts) >= 2:
                last_name = parts[0]
                first_name = parts[1]
                middle_name = parts[2] if len(parts) > 2 else None
            else:
                # Если формат неправильный, используем как есть
                last_name = fio
                first_name = ""
                middle_name = None
            
            updates.append("first_name = %s, last_name = %s, middle_name = %s")
            params.extend([first_name, last_name, middle_name])
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
    def get_user_messages(user_id: int, status: Optional[str] = None, 
                         group_id: Optional[int] = None) -> List[Dict]:
        """Получить все сообщения для пользователя (от кого угодно)"""
        conditions = ["to_user_id = %s"]
        params = [user_id]
        
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
                TRIM(CONCAT_WS(' ', u1.last_name, u1.first_name, u1.middle_name)) as from_user_fio,
                u1.role as from_user_role,
                m.to_user_id,
                TRIM(CONCAT_WS(' ', u2.last_name, u2.first_name, u2.middle_name)) as to_user_fio,
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
    def get_teacher_messages(teacher_id: int, status: Optional[str] = None, 
                            group_id: Optional[int] = None) -> List[Dict]:
        """Получить сообщения для преподавателя от студентов (для обратной совместимости)"""
        return Message.get_user_messages(teacher_id, status, group_id)
    
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
    def get_teacher_stats(user_id: int) -> Dict:
        """Получить статистику сообщений для пользователя"""
        query = """
            SELECT 
                status,
                COUNT(*) as count
            FROM messages
            WHERE to_user_id = %s
            GROUP BY status
        """
        results = execute_query(query, (user_id,), fetch_all=True) or []
        
        stats = {
            'unread': 0,
            'read': 0,
            'total': 0
        }
        
        for row in results:
            status = row.get('status', 'unread')
            count = row.get('count', 0)
            if status in stats:
                stats[status] = count
            stats['total'] += count
        
        return stats


class SupportTicket:
    @staticmethod
    def create_ticket(user_id: int, subject: str, message: str) -> Optional[int]:
        """Создать обращение в поддержку"""
        query = """
            INSERT INTO support_tickets (user_id, subject, message, status)
            VALUES (%s, %s, %s, 'new')
            RETURNING id
        """
        result = execute_query(query, (user_id, subject, message), fetch_one=True)
        return result.get('id') if result else None
    
    @staticmethod
    def get_tickets(status: Optional[str] = None, admin_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        """Получить обращения в поддержку"""
        query = """
            SELECT st.id, st.user_id, st.subject, st.message, st.status, 
                   st.admin_id, st.response_time, st.resolved_at, st.created_at,
                   TRIM(CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name)) as fio, u.max_user_id, u.role
            FROM support_tickets st
            JOIN users u ON st.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND st.status = %s"
            params.append(status)
        
        if admin_id:
            query += " AND st.admin_id = %s"
            params.append(admin_id)
        
        query += " ORDER BY st.created_at DESC LIMIT %s"
        params.append(limit)
        
        return execute_query(query, tuple(params), fetch_all=True) or []
    
    @staticmethod
    def get_ticket_by_id(ticket_id: int) -> Optional[Dict]:
        """Получить обращение по ID"""
        query = """
            SELECT st.id, st.user_id, st.subject, st.message, st.status,
                   st.admin_id, st.response_time, st.resolved_at, st.created_at,
                   TRIM(CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name)) as fio, u.max_user_id, u.role,
                   TRIM(CONCAT_WS(' ', admin_user.last_name, admin_user.first_name, admin_user.middle_name)) as admin_fio
            FROM support_tickets st
            JOIN users u ON st.user_id = u.id
            LEFT JOIN users admin_user ON st.admin_id = admin_user.id
            WHERE st.id = %s
        """
        return execute_query(query, (ticket_id,), fetch_one=True)
    
    @staticmethod
    def update_status(ticket_id: int, status: str, admin_id: Optional[int] = None) -> bool:
        """Обновить статус обращения"""
        params = [status]
        
        if admin_id:
            query = """
                UPDATE support_tickets
                SET status = %s, admin_id = %s, updated_at = CURRENT_TIMESTAMP
            """
            params.append(admin_id)
        else:
            query = """
                UPDATE support_tickets
                SET status = %s, admin_id = NULL, updated_at = CURRENT_TIMESTAMP
            """
        
        if status == 'resolved':
            query = query.replace("updated_at = CURRENT_TIMESTAMP", 
                                 "updated_at = CURRENT_TIMESTAMP, resolved_at = CURRENT_TIMESTAMP")
        
        query += " WHERE id = %s"
        params.append(ticket_id)
        
        execute_query(query, tuple(params))
        return True
    
    @staticmethod
    def set_response_time(ticket_id: int, response_time: int) -> bool:
        """Установить время реакции (в минутах)"""
        query = """
            UPDATE support_tickets
            SET response_time = %s
            WHERE id = %s AND response_time IS NULL
        """
        execute_query(query, (response_time, ticket_id))
        return True
    
    @staticmethod
    def get_stats() -> Dict:
        """Получить статистику по обращениям"""
        query = """
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'new') as new,
                COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
                COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
                AVG(response_time) as avg_response_time,
                COUNT(*) FILTER (WHERE resolved_at IS NOT NULL) as total_resolved
            FROM support_tickets
        """
        result = execute_query(query, (), fetch_one=True) or {}
        return {
            'total': result.get('total', 0) or 0,
            'new': result.get('new', 0) or 0,
            'in_progress': result.get('in_progress', 0) or 0,
            'resolved': result.get('resolved', 0) or 0,
            'avg_response_time': float(result.get('avg_response_time', 0) or 0),
            'total_resolved': result.get('total_resolved', 0) or 0
        }


class FAQ:
    @staticmethod
    def get_faq(category: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Получить FAQ"""
        query = """
            SELECT id, question, answer, category, created_at
            FROM faq
            WHERE 1=1
        """
        params = []
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        return execute_query(query, tuple(params), fetch_all=True) or []
    
    @staticmethod
    def get_faq_by_id(faq_id: int) -> Optional[Dict]:
        """Получить FAQ по ID"""
        query = """
            SELECT id, question, answer, category, created_at
            FROM faq
            WHERE id = %s
        """
        return execute_query(query, (faq_id,), fetch_one=True)
    
    @staticmethod
    def create_faq(question: str, answer: str, category: str = 'general', created_by: Optional[int] = None) -> Optional[int]:
        """Создать FAQ"""
        query = """
            INSERT INTO faq (question, answer, category, created_by)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        result = execute_query(query, (question, answer, category, created_by), fetch_one=True)
        return result.get('id') if result else None
    
    @staticmethod
    def update_faq(faq_id: int, question: str, answer: str, category: str = 'general') -> bool:
        """Обновить FAQ"""
        query = """
            UPDATE faq
            SET question = %s, answer = %s, category = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        execute_query(query, (question, answer, category, faq_id))
        return True
    
    @staticmethod
    def delete_faq(faq_id: int) -> bool:
        """Удалить FAQ"""
        query = "DELETE FROM faq WHERE id = %s"
        execute_query(query, (faq_id,))
        return True


class AdminMessage:
    @staticmethod
    def create_message(admin_id: int, title: str, message: str, target_role: Optional[str] = None, target_group_id: Optional[int] = None) -> Optional[int]:
        """Создать сообщение администрации"""
        query = """
            INSERT INTO admin_messages (admin_id, title, message, target_role, target_group_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        result = execute_query(query, (admin_id, title, message, target_role, target_group_id), fetch_one=True)
        return result.get('id') if result else None
    
    @staticmethod
    def get_messages(limit: int = 50) -> List[Dict]:
        """Получить сообщения администрации"""
        query = """
            SELECT am.id, am.title, am.message, am.target_role, am.target_group_id,
                   am.sent_at, am.created_at,
                   TRIM(CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name)) as admin_fio,
                   g.name as group_name
            FROM admin_messages am
            LEFT JOIN users u ON am.admin_id = u.id
            LEFT JOIN groups g ON am.target_group_id = g.id
            ORDER BY am.created_at DESC
            LIMIT %s
        """
        return execute_query(query, (limit,), fetch_all=True) or []


class News:
    @staticmethod
    def get_news_by_role(user_role: str, user_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        """Получить новости для пользователя по его роли
        
        Логика:
        - Если target_role = 'all' или NULL - показывать всем
        - Если target_role = user_role - показывать пользователям этой роли
        - Если target_group_id указан - показывать только пользователям этой группы
        """
        # Получаем группы пользователя
        user_group_ids = []
        if user_id:
            if user_role == 'student':
                user_groups = Group.get_user_groups(user_id)
                user_group_ids = [g['id'] for g in user_groups]
            elif user_role == 'teacher':
                user_groups = Teacher.get_teacher_groups(user_id)
                user_group_ids = [g['id'] for g in user_groups]
        
        # Формируем условия для WHERE
        conditions = []
        params = []
        
        # Условие для target_role: 'all', NULL или совпадает с ролью пользователя
        conditions.append("(target_role IS NULL OR target_role = 'all' OR target_role = %s)")
        params.append(user_role)
        
        # Если у пользователя есть группы, добавляем условие для target_group_id
        if user_group_ids:
            conditions.append("(target_group_id IS NULL OR target_group_id = ANY(%s))")
            params.append(user_group_ids)
        else:
            # Если у пользователя нет групп, показываем только новости без target_group_id
            conditions.append("target_group_id IS NULL")
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT id, title, description, hashtags, target_role, target_group_id, created_at
            FROM news
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s
        """
        params.append(limit)
        
        return execute_query(query, tuple(params), fetch_all=True) or []

