-- SQL скрипт для заполнения базы данных тестовыми данными
-- Использование: psql -U maxbot -d maxbot_db -f seed_data.sql

-- ============================================
-- ГРУППЫ
-- ============================================

-- Добавить группу ИКБО-16-22
INSERT INTO groups (name, semester, year) VALUES ('ИКБО-16-22', 7, 2025);

-- Добавить группу ИКБО-16-21
INSERT INTO groups (name, semester, year) VALUES ('ИКБО-16-21', 7, 2025);

-- Добавить группу ИКБО-16-23
INSERT INTO groups (name, semester, year) VALUES ('ИКБО-16-23', 7, 2025);

-- Добавить группу ИКБО-17-21
INSERT INTO groups (name, semester, year) VALUES ('ИКБО-17-21', 5, 2025);

-- Добавить группу ИКБО-17-22
INSERT INTO groups (name, semester, year) VALUES ('ИКБО-17-22', 5, 2025);

-- Добавить группу ИКБО-18-21
INSERT INTO groups (name, semester, year) VALUES ('ИКБО-18-21', 3, 2025);

-- Добавить группу ИКБО-18-22
INSERT INTO groups (name, semester, year) VALUES ('ИКБО-18-22', 3, 2025);

-- ============================================
-- СТУДЕНТЫ
-- ============================================

-- Добавить студента (староста группы ИКБО-16-22)
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855100, 'Георгий', 'Пархоменко', 'Дмитриевич', 'student', '+79001234567', 'parhomenko@example.com');

-- Добавить студента в группу ИКБО-16-22 как старосту
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (1, 1, true);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855101, 'Дарья', 'Чугунова', 'Игоревна', 'student', '+79001234568', 'chugunova@example.com');

-- Добавить студента в группу ИКБО-16-22
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (2, 1, false);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855102, 'Иван', 'Иванов', 'Иванович', 'student', '+79001234569', 'ivanov@example.com');

-- Добавить студента в группу ИКБО-16-22
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (3, 1, false);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855103, 'Петр', 'Петров', 'Петрович', 'student', '+79001234570', 'petrov@example.com');

-- Добавить студента в группу ИКБО-16-21
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (4, 2, true);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855104, 'Мария', 'Сидорова', 'Сидоровна', 'student', '+79001234571', 'sidorova@example.com');

-- Добавить студента в группу ИКБО-16-21
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (5, 2, false);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855105, 'Александр', 'Смирнов', 'Александрович', 'student', '+79001234572', 'smirnov@example.com');

-- Добавить студента в группу ИКБО-16-22
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (6, 1, false);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855106, 'Екатерина', 'Козлова', 'Сергеевна', 'student', '+79001234573', 'kozlova@example.com');

-- Добавить студента в группу ИКБО-16-22
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (7, 1, false);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855107, 'Дмитрий', 'Новиков', 'Владимирович', 'student', '+79001234574', 'novikov@example.com');

-- Добавить студента в группу ИКБО-16-23
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (8, 3, true);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855108, 'Анна', 'Морозова', 'Ивановна', 'student', '+79001234575', 'morozova@example.com');

-- Добавить студента в группу ИКБО-16-23
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (9, 3, false);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855109, 'Максим', 'Петров', 'Андреевич', 'student', '+79001234576', 'petrov2@example.com');

-- Добавить студента в группу ИКБО-17-21
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (10, 4, true);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855110, 'София', 'Волкова', 'Дмитриевна', 'student', '+79001234577', 'volkova@example.com');

-- Добавить студента в группу ИКБО-17-21
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (11, 4, false);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855111, 'Артем', 'Соколов', 'Николаевич', 'student', '+79001234578', 'sokolov@example.com');

-- Добавить студента в группу ИКБО-17-22
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (12, 5, true);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855112, 'Виктория', 'Лебедева', 'Александровна', 'student', '+79001234579', 'lebedeva@example.com');

-- Добавить студента в группу ИКБО-17-22
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (13, 5, false);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855113, 'Илья', 'Егоров', 'Сергеевич', 'student', '+79001234580', 'egorov@example.com');

-- Добавить студента в группу ИКБО-18-21
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (14, 6, true);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855114, 'Полина', 'Павлова', 'Владимировна', 'student', '+79001234581', 'pavlova@example.com');

-- Добавить студента в группу ИКБО-18-21
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (15, 6, false);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855115, 'Кирилл', 'Козлов', 'Андреевич', 'student', '+79001234582', 'kozlov2@example.com');

-- Добавить студента в группу ИКБО-18-22
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (16, 7, true);

-- Добавить студента
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855116, 'Алиса', 'Новикова', 'Игоревна', 'student', '+79001234583', 'novikova@example.com');

-- Добавить студента в группу ИКБО-18-22
INSERT INTO group_members (user_id, group_id, is_headman)
VALUES (17, 7, false);

-- ============================================
-- ПРЕПОДАВАТЕЛИ
-- ============================================

-- Добавить преподавателя
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855100, 'Михаил', 'Волков', 'Юрьевич', 'teacher', '+79007654321', 'volkov@example.com');

-- Назначить преподавателя группе ИКБО-16-22
-- Примечание: ID преподавателя будет 18 (после 17 студентов)
INSERT INTO teacher_groups (teacher_id, group_id, semester, year)
VALUES (18, 1, 7, 2025);

-- Назначить преподавателя группе ИКБО-16-21
INSERT INTO teacher_groups (teacher_id, group_id, semester, year)
VALUES (18, 2, 7, 2025);

-- Добавить преподавателя
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (88287732, 'Анна', 'Смирнова', 'Александровна', 'teacher', '+79007654322', 'smirnova@example.com');

-- Назначить преподавателя группе ИКБО-16-22
-- Примечание: ID преподавателя будет 19
INSERT INTO teacher_groups (teacher_id, group_id, semester, year)
VALUES (19, 1, 7, 2025);

-- Добавить преподавателя
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (88287733, 'Сергей', 'Кузнецов', 'Владимирович', 'teacher', '+79007654323', 'kuznetsov@example.com');

-- Назначить преподавателя группе ИКБО-16-23
-- Примечание: ID преподавателя будет 20
INSERT INTO teacher_groups (teacher_id, group_id, semester, year)
VALUES (20, 3, 7, 2025);

-- Добавить преподавателя
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (88287734, 'Ольга', 'Петрова', 'Викторовна', 'teacher', '+79007654326', 'petrova@example.com');

-- Назначить преподавателя группе ИКБО-17-21
-- Примечание: ID преподавателя будет 21
INSERT INTO teacher_groups (teacher_id, group_id, semester, year)
VALUES (21, 4, 5, 2025);

-- Назначить преподавателя группе ИКБО-17-22
INSERT INTO teacher_groups (teacher_id, group_id, semester, year)
VALUES (21, 5, 5, 2025);

-- Добавить преподавателя
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (88287735, 'Алексей', 'Иванов', 'Михайлович', 'teacher', '+79007654327', 'ivanov2@example.com');

-- Назначить преподавателя группе ИКБО-18-21
-- Примечание: ID преподавателя будет 22
INSERT INTO teacher_groups (teacher_id, group_id, semester, year)
VALUES (22, 6, 3, 2025);

-- Назначить преподавателя группе ИКБО-18-22
INSERT INTO teacher_groups (teacher_id, group_id, semester, year)
VALUES (22, 7, 3, 2025);

-- Добавить преподавателя
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (88287736, 'Елена', 'Федорова', 'Анатольевна', 'teacher', '+79007654328', 'fedorova@example.com');

-- Назначить преподавателя группе ИКБО-16-21
-- Примечание: ID преподавателя будет 23
INSERT INTO teacher_groups (teacher_id, group_id, semester, year)
VALUES (23, 2, 7, 2025);

-- Назначить преподавателя группе ИКБО-17-21
INSERT INTO teacher_groups (teacher_id, group_id, semester, year)
VALUES (23, 4, 5, 2025);

-- ============================================
-- АДМИНИСТРАТОР
-- ============================================

-- Добавить администратора
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855100, 'Админ', 'Админов', 'Админович', 'admin', '+79007654324', 'admin@example.com');

-- ============================================
-- ПОДДЕРЖКА
-- ============================================

-- Добавить сотрудника поддержки
INSERT INTO users (max_user_id, first_name, last_name, middle_name, role, phone, email)
VALUES (96855100, 'Поддержка', 'Поддержковая', 'Поддержковна', 'support', '+79007654325', 'support@example.com');

-- ============================================
-- НОВОСТИ (опционально)
-- ============================================

-- Добавить новость для всех студентов
-- Примечание: created_by = 24 (ID администратора: 17 студентов + 6 преподавателей + 1 администратор = 24)
INSERT INTO news (title, description, hashtags, target_role, target_group_id, created_by)
VALUES ('Добро пожаловать!', 'Добро пожаловать в цифровую образовательную платформу MAX!', '#новость #приветствие', 'student', NULL, 24);

-- Добавить новость для конкретной группы
INSERT INTO news (title, description, hashtags, target_role, target_group_id, created_by)
VALUES ('Важная информация для ИКБО-16-22', 'Напоминаем о сдаче лабораторных работ до конца недели.', '#лабораторные #ИКБО-16-22', 'student', 1, 24);

-- Добавить новость для преподавателей
INSERT INTO news (title, description, hashtags, target_role, target_group_id, created_by)
VALUES ('Собрание преподавателей', 'Собрание преподавателей состоится в пятницу в 15:00.', '#собрание #преподаватели', 'teacher', NULL, 24);

-- Добавить новость для всех
INSERT INTO news (title, description, hashtags, target_role, target_group_id, created_by)
VALUES ('Обновление системы', 'В системе появились новые функции для работы с расписанием.', '#обновление #новые_функции', NULL, NULL, 24);

-- Добавить новость для группы ИКБО-16-21
INSERT INTO news (title, description, hashtags, target_role, target_group_id, created_by)
VALUES ('Консультация по курсовой', 'Консультация по курсовой работе для группы ИКБО-16-21 пройдет в среду.', '#консультация #курсовая', 'student', 2, 24);

-- Добавить новость для группы ИКБО-17-21
INSERT INTO news (title, description, hashtags, target_role, target_group_id, created_by)
VALUES ('Экзамен по программированию', 'Экзамен по программированию для группы ИКБО-17-21 назначен на следующую неделю.', '#экзамен #программирование', 'student', 4, 24);

-- Добавить новость для всех студентов
INSERT INTO news (title, description, hashtags, target_role, target_group_id, created_by)
VALUES ('Начало нового семестра', 'Поздравляем с началом нового семестра! Желаем успехов в учебе.', '#семестр #поздравление', 'student', NULL, 24);

-- ============================================
-- СООБЩЕНИЯ (опционально)
-- ============================================

-- Добавить сообщение от преподавателя студенту
-- Примечание: преподаватель ID = 18 (первый преподаватель)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (18, 1, 'Привет! Напоминаю о консультации завтра в 14:00.', 'unread');

-- Добавить сообщение от студента преподавателю
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (1, 18, 'Здравствуйте! У меня вопрос по лабораторной работе.', 'unread');

-- Добавить сообщение от группы (староста от имени группы)
INSERT INTO messages (from_user_id, to_user_id, group_id, text, status)
VALUES (1, 18, 1, 'От группы ИКБО-16-22: можем ли мы перенести консультацию?', 'unread');

-- Добавить сообщение от преподавателя студенту
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (18, 2, 'Добрый день! Напоминаю о дедлайне по лабораторной работе №3.', 'unread');

-- Добавить сообщение от студента преподавателю
-- Примечание: преподаватель ID = 19 (второй преподаватель)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (3, 19, 'Здравствуйте! Можно ли получить консультацию по проекту?', 'unread');

-- Добавить сообщение от преподавателя студенту (прочитано)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (19, 3, 'Конечно! Приходите в четверг с 14:00 до 16:00.', 'read');

-- Добавить сообщение от старосты группы преподавателю
INSERT INTO messages (from_user_id, to_user_id, group_id, text, status)
VALUES (4, 18, 2, 'От группы ИКБО-16-21: у нас вопрос по расписанию на следующую неделю.', 'unread');

-- Добавить сообщение от преподавателя группе
-- Примечание: преподаватель ID = 20 (третий преподаватель)
INSERT INTO messages (from_user_id, to_user_id, group_id, text, status)
VALUES (20, 8, 3, 'Всем студентам группы ИКБО-16-23: экзамен переносится на следующую неделю.', 'unread');

-- Добавить сообщение от студента старосте
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (2, 1, 'Привет! Когда будет собрание группы?', 'read');

-- Добавить сообщение от старосты студенту
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (1, 2, 'Собрание будет в пятницу после пар.', 'read');

-- Добавить сообщение от преподавателя студенту
-- Примечание: преподаватель ID = 21 (четвертый преподаватель)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (21, 10, 'Добро пожаловать в новую группу! Расписание занятий уже доступно.', 'unread');

-- Добавить сообщение от студента преподавателю
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (11, 21, 'Спасибо! Вопрос: где можно найти материалы к лекциям?', 'unread');

-- ============================================
-- СООБЩЕНИЯ ДЛЯ АДМИНИСТРАТОРА
-- ============================================

-- Добавить сообщение от студента администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (1, 24, 'Здравствуйте! У меня вопрос: можно ли добавить еще одного студента в нашу группу?', 'unread');

-- Добавить сообщение от студента администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (2, 24, 'Добрый день! Прошу помочь с изменением данных в профиле.', 'unread');

-- Добавить сообщение от преподавателя администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (18, 24, 'Здравствуйте! Нужна помощь с назначением меня на новую группу.', 'unread');

-- Добавить сообщение от студента администратору (прочитано)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (3, 24, 'Вопрос по расписанию: можно ли изменить время консультации?', 'read');

-- Добавить сообщение от старосты группы администратору
INSERT INTO messages (from_user_id, to_user_id, group_id, text, status)
VALUES (1, 24, 1, 'От группы ИКБО-16-22: просим добавить нового студента в нашу группу.', 'unread');

-- Добавить сообщение от преподавателя администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (19, 24, 'Добрый день! Нужна помощь с настройкой доступа к группе.', 'unread');

-- Добавить сообщение от студента администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (5, 24, 'Здравствуйте! У меня проблема с отображением моей группы в системе.', 'unread');

-- Добавить сообщение от старосты группы администратору
INSERT INTO messages (from_user_id, to_user_id, group_id, text, status)
VALUES (4, 24, 2, 'От группы ИКБО-16-21: просим обновить информацию о группе.', 'unread');

-- Добавить сообщение от преподавателя администратору (прочитано)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (20, 24, 'Спасибо за помощь с настройкой! Все работает отлично.', 'read');

-- Добавить сообщение от студента администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (7, 24, 'Вопрос: как изменить старосту группы?', 'unread');

-- Добавить сообщение от студента администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (8, 24, 'Здравствуйте! Прошу помочь с добавлением нового студента в нашу группу ИКБО-16-23.', 'unread');

-- Добавить сообщение от преподавателя администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (21, 24, 'Добрый день! Нужна помощь с назначением меня на группу ИКБО-18-21.', 'unread');

-- Добавить сообщение от студента администратору (прочитано)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (9, 24, 'Спасибо за помощь! Все работает отлично.', 'read');

-- Добавить сообщение от старосты группы администратору
INSERT INTO messages (from_user_id, to_user_id, group_id, text, status)
VALUES (10, 24, 4, 'От группы ИКБО-17-21: просим обновить информацию о семестре.', 'unread');

-- Добавить сообщение от преподавателя администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (22, 24, 'Здравствуйте! У меня вопрос по доступу к группе ИКБО-18-22.', 'unread');

-- Добавить сообщение от студента администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (11, 24, 'Добрый день! Не могу найти свою группу в списке.', 'unread');

-- Добавить сообщение от старосты группы администратору
INSERT INTO messages (from_user_id, to_user_id, group_id, text, status)
VALUES (12, 24, 5, 'От группы ИКБО-17-22: просим добавить нового студента.', 'unread');

-- Добавить сообщение от преподавателя администратору (прочитано)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (23, 24, 'Спасибо за быструю помощь! Проблема решена.', 'read');

-- Добавить сообщение от студента администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (13, 24, 'Вопрос: можно ли изменить название группы?', 'unread');

-- Добавить сообщение от студента администратору
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (14, 24, 'Здравствуйте! У меня проблема с отображением данных в профиле.', 'unread');

-- Добавить сообщение от старосты группы администратору
INSERT INTO messages (from_user_id, to_user_id, group_id, text, status)
VALUES (16, 24, 7, 'От группы ИКБО-18-22: просим обновить список студентов.', 'unread');

-- ============================================
-- ОБРАЩЕНИЯ В ПОДДЕРЖКУ (опционально)
-- ============================================

-- Добавить обращение в поддержку
INSERT INTO support_tickets (user_id, subject, message, status)
VALUES (1, 'Проблема с авторизацией', 'Не могу войти в систему. Показывает ошибку авторизации.', 'new');

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (1, 25, 'Не могу войти в систему. Показывает ошибку авторизации.', 'unread');

-- Добавить обращение в поддержку
INSERT INTO support_tickets (user_id, subject, message, status)
VALUES (2, 'Вопрос по расписанию', 'Как изменить расписание?', 'new');

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (2, 25, 'Как изменить расписание?', 'unread');

-- Добавить обращение в поддержку (в работе)
-- Примечание: admin_id = 25 (ID поддержки: 17 студентов + 6 преподавателей + 1 администратор + 1 поддержка = 25)
INSERT INTO support_tickets (user_id, subject, message, status, admin_id)
VALUES (3, 'Проблема с отображением', 'Проблема с отображением расписания на мобильном устройстве.', 'in_progress', 25);

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (3, 25, 'Проблема с отображением расписания на мобильном устройстве.', 'read');

-- Добавить обращение в поддержку
INSERT INTO support_tickets (user_id, subject, message, status)
VALUES (5, 'Поиск информации о группе', 'Не могу найти информацию о своей группе в системе.', 'new');

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (5, 25, 'Не могу найти информацию о своей группе в системе.', 'unread');

-- Добавить обращение в поддержку
INSERT INTO support_tickets (user_id, subject, message, status)
VALUES (7, 'Изменение профиля', 'Как изменить свой профиль?', 'new');

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (7, 25, 'Как изменить свой профиль?', 'unread');

-- Добавить обращение в поддержку (в работе)
INSERT INTO support_tickets (user_id, subject, message, status, admin_id)
VALUES (9, 'Ошибка отправки сообщения', 'Ошибка при отправке сообщения преподавателю.', 'in_progress', 25);

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (9, 25, 'Ошибка при отправке сообщения преподавателю.', 'read');

-- Добавить обращение в поддержку (решено)
INSERT INTO support_tickets (user_id, subject, message, status, admin_id, resolved_at)
VALUES (12, 'Вопрос по использованию бота', 'Вопрос по использованию бота. Уже решено.', 'resolved', 25, CURRENT_TIMESTAMP);

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (12, 25, 'Вопрос по использованию бота. Уже решено.', 'read');

-- Добавить обращение в поддержку
INSERT INTO support_tickets (user_id, subject, message, status)
VALUES (14, 'Проблема с уведомлениями', 'Не приходят уведомления о новых сообщениях.', 'new');

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (14, 25, 'Не приходят уведомления о новых сообщениях.', 'unread');

-- Добавить обращение в поддержку (решено)
INSERT INTO support_tickets (user_id, subject, message, status, admin_id, resolved_at)
VALUES (16, 'Проблема с авторизацией', 'Проблема с авторизацией. Проблема решена.', 'resolved', 25, CURRENT_TIMESTAMP);

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (16, 25, 'Проблема с авторизацией. Проблема решена.', 'read');

-- Добавить обращение в поддержку
INSERT INTO support_tickets (user_id, subject, message, status)
VALUES (17, 'Связь с администрацией', 'Как связаться с администрацией?', 'new');

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (17, 25, 'Как связаться с администрацией?', 'unread');

-- Добавить обращение в поддержку
INSERT INTO support_tickets (user_id, subject, message, status)
VALUES (6, 'Проблема с загрузкой расписания', 'Расписание не загружается, показывает ошибку 404.', 'new');

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (6, 25, 'Расписание не загружается, показывает ошибку 404.', 'unread');

-- Добавить обращение в поддержку
INSERT INTO support_tickets (user_id, subject, message, status)
VALUES (8, 'Вопрос по новостям', 'Не вижу новости для моей группы. Это нормально?', 'new');

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (8, 25, 'Не вижу новости для моей группы. Это нормально?', 'unread');

-- Добавить обращение в поддержку (в работе)
INSERT INTO support_tickets (user_id, subject, message, status, admin_id)
VALUES (10, 'Ошибка при отправке сообщения', 'При попытке отправить сообщение преподавателю возникает ошибка.', 'in_progress', 25);

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (10, 25, 'При попытке отправить сообщение преподавателю возникает ошибка.', 'read');

-- Добавить обращение в поддержку
INSERT INTO support_tickets (user_id, subject, message, status)
VALUES (13, 'Не могу найти свою группу', 'В списке групп нет моей группы ИКБО-17-22.', 'new');

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (13, 25, 'В списке групп нет моей группы ИКБО-17-22.', 'unread');

-- Добавить обращение в поддержку (решено)
INSERT INTO support_tickets (user_id, subject, message, status, admin_id, resolved_at)
VALUES (15, 'Вопрос по профилю', 'Как изменить email в профиле? Проблема решена.', 'resolved', 25, CURRENT_TIMESTAMP);

-- Добавить сообщение в поддержку (соответствует тикету выше)
INSERT INTO messages (from_user_id, to_user_id, text, status)
VALUES (15, 25, 'Как изменить email в профиле? Проблема решена.', 'read');

-- ============================================
-- КОММЕНТАРИИ
-- ============================================

-- Примечания:
-- 1. ID пользователей автоматически генерируются при INSERT
-- 2. Если нужно использовать конкретные ID, используйте явное указание:
--    INSERT INTO users (id, max_user_id, ...) VALUES (1, 96855100, ...);
-- 3. max_user_id может повторяться для разных ролей одного пользователя
-- 4. Для добавления пользователя в несколько групп используйте несколько INSERT в group_members
-- 5. Для назначения преподавателя на несколько групп используйте несколько INSERT в teacher_groups

