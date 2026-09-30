"""
TwinStudy AI - Relational Database Manager (MySQL + PyMySQL with SQLite Fallback)
Supports high-availability relational persistence, secure password hashing,
session tokens, and user-scoped data access.
"""

import os
import json
import uuid
import datetime
import sqlite3
import pymysql
from pymysql.cursors import DictCursor
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration from Environment
MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "twinstudy")

IS_VERCEL = bool(os.environ.get("VERCEL"))
if IS_VERCEL:
    SQLITE_PATH = "/tmp/twin_relational.db"
    LEGACY_JSON_PATH = "/tmp/twin_database.json"
    bundled_sqlite = os.path.join(os.path.dirname(__file__), "twin_relational.db")
    bundled_json = os.path.join(os.path.dirname(__file__), "twin_database.json")
    import shutil
    if not os.path.exists(SQLITE_PATH) and os.path.exists(bundled_sqlite):
        try:
            shutil.copyfile(bundled_sqlite, SQLITE_PATH)
        except Exception:
            pass
    if not os.path.exists(LEGACY_JSON_PATH) and os.path.exists(bundled_json):
        try:
            shutil.copyfile(bundled_json, LEGACY_JSON_PATH)
        except Exception:
            pass
else:
    SQLITE_PATH = os.path.join(os.path.dirname(__file__), "twin_relational.db")
    LEGACY_JSON_PATH = os.path.join(os.path.dirname(__file__), "twin_database.json")

def safe_int(val, default=0):
    try:
        if val is None or val == "":
            return default
        return int(val)
    except Exception:
        return default

def safe_float(val, default=0.0):
    try:
        if val is None or val == "":
            return default
        return float(val)
    except Exception:
        return default

class DatabaseManager:
    def __init__(self):
        self.engine_type = "sqlite"
        self._test_mysql_and_init()

    def _test_mysql_and_init(self):
        try:
            # Try connecting to MySQL server
            conn = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                connect_timeout=2
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.commit()
            conn.close()
            self.engine_type = "mysql"
            print(f"[DB] Successfully connected to MySQL at {MYSQL_HOST}:{MYSQL_PORT}, database: {MYSQL_DATABASE}")
        except Exception as e:
            self.engine_type = "sqlite"
            print(f"[DB] MySQL server not reachable ({e}). Using robust Relational SQLite engine at {SQLITE_PATH}")

        self.init_schema()
        self.migrate_from_json_if_needed()

    def get_connection(self):
        if self.engine_type == "mysql":
            return pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                cursorclass=DictCursor,
                autocommit=True
            )
        else:
            conn = sqlite3.connect(SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn

    def execute(self, query: str, params=()):
        conn = self.get_connection()
        try:
            if self.engine_type == "sqlite":
                # Convert %s to ? for SQLite
                sqlite_query = query.replace("%s", "?")
                cur = conn.cursor()
                cur.execute(sqlite_query, params)
                conn.commit()
                return cur
            else:
                cur = conn.cursor()
                cur.execute(query, params)
                return cur
        finally:
            if self.engine_type == "sqlite":
                conn.close()
            else:
                conn.close()

    def fetchone(self, query: str, params=()):
        conn = self.get_connection()
        try:
            if self.engine_type == "sqlite":
                sqlite_query = query.replace("%s", "?")
                cur = conn.cursor()
                cur.execute(sqlite_query, params)
                row = cur.fetchone()
                return dict(row) if row else None
            else:
                cur = conn.cursor()
                cur.execute(query, params)
                return cur.fetchone()
        finally:
            conn.close()

    def fetchall(self, query: str, params=()):
        conn = self.get_connection()
        try:
            if self.engine_type == "sqlite":
                sqlite_query = query.replace("%s", "?")
                cur = conn.cursor()
                cur.execute(sqlite_query, params)
                rows = cur.fetchall()
                return [dict(r) for r in rows]
            else:
                cur = conn.cursor()
                cur.execute(query, params)
                return cur.fetchall()
        finally:
            conn.close()

    def init_schema(self):
        """Creates all 17 tables with relational integrity."""
        # Using dialect-neutral SQL where possible
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(64) PRIMARY KEY,
                email VARCHAR(191) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(191),
                role VARCHAR(32) DEFAULT 'student',
                dob VARCHAR(32),
                age INT DEFAULT 20,
                is_minor INT DEFAULT 0,
                points INT DEFAULT 100,
                streak_days INT DEFAULT 1,
                daily_study_hours REAL DEFAULT 3.0,
                focus_duration_minutes INT DEFAULT 45,
                learning_preference TEXT,
                preferred_study_time VARCHAR(64) DEFAULT 'Evening',
                college VARCHAR(191),
                grade_level VARCHAR(191),
                guardian_email VARCHAR(191),
                linking_code VARCHAR(64),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS student_profiles (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                student_name VARCHAR(191),
                college VARCHAR(191),
                course VARCHAR(191),
                semester VARCHAR(64),
                specialization VARCHAR(64) DEFAULT 'cs',
                academic_year VARCHAR(64) DEFAULT '2026-2027',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS subjects (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                name VARCHAR(191) NOT NULL,
                code VARCHAR(64),
                credits INT DEFAULT 3,
                target_percentage REAL DEFAULT 85.0,
                professor VARCHAR(191),
                teacher VARCHAR(191),
                room VARCHAR(64),
                color VARCHAR(32) DEFAULT '#3b82f6',
                type VARCHAR(64) DEFAULT 'Lecture',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS classes (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                subject_id VARCHAR(64),
                subject_name VARCHAR(191),
                subject VARCHAR(191),
                day VARCHAR(32) NOT NULL,
                time_slot VARCHAR(64) NOT NULL,
                time VARCHAR(64),
                start_time VARCHAR(32),
                end_time VARCHAR(32),
                room VARCHAR(64),
                professor VARCHAR(191),
                teacher VARCHAR(191),
                color VARCHAR(32) DEFAULT '#3b82f6',
                type VARCHAR(64) DEFAULT 'Lecture',
                week_type VARCHAR(64) DEFAULT 'All',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                subject_id VARCHAR(64),
                subject_name VARCHAR(191),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                due_date VARCHAR(64),
                priority VARCHAR(32) DEFAULT 'medium',
                status VARCHAR(64) DEFAULT 'Pending',
                points_reward INT DEFAULT 100,
                verified INT DEFAULT 0,
                verified_file VARCHAR(255),
                quiz_score VARCHAR(32),
                verified_at VARCHAR(64),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS exams (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                subject_id VARCHAR(64),
                subject_name VARCHAR(191),
                title VARCHAR(255) NOT NULL,
                exam_date VARCHAR(64),
                weight_pct REAL DEFAULT 30.0,
                target_score REAL DEFAULT 85.0,
                syllabus_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS grades (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                subject_id VARCHAR(64),
                subject_name VARCHAR(191),
                assessment_type VARCHAR(64),
                title VARCHAR(255),
                marks_obtained REAL,
                max_marks REAL,
                percentage REAL,
                grade VARCHAR(16),
                term VARCHAR(64),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS study_sessions (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                subject_name VARCHAR(191),
                duration_minutes INT,
                focus_score REAL,
                stamina_start REAL,
                stamina_end REAL,
                date VARCHAR(64),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS goals (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                title VARCHAR(255),
                category VARCHAR(64),
                target_date VARCHAR(64),
                status VARCHAR(64) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS behavior_patterns (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                title VARCHAR(255),
                pattern_type VARCHAR(64),
                confidence REAL DEFAULT 85.0,
                evidence_count INT DEFAULT 1,
                evidence_summary TEXT,
                weight REAL DEFAULT 1.0,
                is_active INT DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS decisions (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                question TEXT,
                baseline_data TEXT,
                simulation_result TEXT,
                recommended_option VARCHAR(191),
                chosen_option VARCHAR(191),
                agreement VARCHAR(32),
                user_reason TEXT,
                outcome_rating INT,
                outcome_feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                decision_id VARCHAR(64),
                feedback_type VARCHAR(64),
                comments TEXT,
                rating INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS permissions (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                guardian_email VARCHAR(191),
                allow_view_study_hours INT DEFAULT 1,
                allow_view_proofs INT DEFAULT 1,
                allow_nudges INT DEFAULT 1,
                approved INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                title VARCHAR(255),
                description TEXT,
                type VARCHAR(64) DEFAULT 'info',
                is_read INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS chat_conversations (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                title VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id VARCHAR(64) PRIMARY KEY,
                conversation_id VARCHAR(64) NOT NULL,
                user_id VARCHAR(64) NOT NULL,
                role VARCHAR(32) NOT NULL,
                content TEXT NOT NULL,
                context_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token VARCHAR(128) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
            """
        ]

        conn = self.get_connection()
        try:
            cur = conn.cursor()
            for stmt in tables:
                cur.execute(stmt)
            if self.engine_type == "sqlite":
                conn.commit()
            print("[DB] Relational schema initialized successfully.")
        finally:
            conn.close()

        self._ensure_columns_exist()

    def _ensure_columns_exist(self):
        """Ensures that all necessary schedule and timetable columns exist without losing existing data."""
        try:
            if self.engine_type == "sqlite":
                conn = self.get_connection()
                try:
                    cur = conn.cursor()
                    cur.execute("PRAGMA table_info(subjects)")
                    cur_cols = [r[1] for r in cur.fetchall()]
                    if "teacher" not in cur_cols:
                        cur.execute("ALTER TABLE subjects ADD COLUMN teacher VARCHAR(191)")
                    if "type" not in cur_cols:
                        cur.execute("ALTER TABLE subjects ADD COLUMN type VARCHAR(64) DEFAULT 'Lecture'")

                    cur.execute("PRAGMA table_info(classes)")
                    cls_cols = [r[1] for r in cur.fetchall()]
                    cols_to_add = [
                        ("subject", "VARCHAR(191)"),
                        ("time", "VARCHAR(64)"),
                        ("start_time", "VARCHAR(32)"),
                        ("end_time", "VARCHAR(32)"),
                        ("teacher", "VARCHAR(191)"),
                        ("type", "VARCHAR(64) DEFAULT 'Lecture'"),
                        ("week_type", "VARCHAR(64) DEFAULT 'All'")
                    ]
                    for col, ctype in cols_to_add:
                        if col not in cls_cols:
                            cur.execute(f"ALTER TABLE classes ADD COLUMN {col} {ctype}")
                    conn.commit()
                finally:
                    conn.close()
            else:
                for col, ctype in [("teacher", "VARCHAR(191)"), ("type", "VARCHAR(64) DEFAULT 'Lecture'")]:
                    try:
                        self.execute(f"ALTER TABLE subjects ADD COLUMN {col} {ctype}")
                    except Exception:
                        pass
                for col, ctype in [
                    ("subject", "VARCHAR(191)"),
                    ("time", "VARCHAR(64)"),
                    ("start_time", "VARCHAR(32)"),
                    ("end_time", "VARCHAR(32)"),
                    ("teacher", "VARCHAR(191)"),
                    ("type", "VARCHAR(64) DEFAULT 'Lecture'"),
                    ("week_type", "VARCHAR(64) DEFAULT 'All'")
                ]:
                    try:
                        self.execute(f"ALTER TABLE classes ADD COLUMN {col} {ctype}")
                    except Exception:
                        pass
        except Exception as e:
            print(f"[DB] Notice during column migration: {e}")

    def migrate_from_json_if_needed(self):
        """Seeds the relational database from twin_database.json if users table is empty."""
        user_count = self.fetchone("SELECT COUNT(*) as cnt FROM users")
        cnt = (user_count.get("cnt") if user_count else 0) or 0
        if cnt > 0:
            return # Already seeded

        if not os.path.exists(LEGACY_JSON_PATH):
            return

        try:
            with open(LEGACY_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[DB] Error loading legacy JSON for migration: {e}")
            return

        print("[DB] Migrating data from twin_database.json to relational database...")
        registered = data.get("registered_users", {})

        # Default student user from json root if not in registered_users
        root_user = data.get("user", {})
        if root_user and root_user.get("email"):
            r_email = root_user.get("email").strip().lower()
            if r_email not in [k.lower() for k in registered.keys()]:
                registered[r_email] = root_user

        # Ensure demo users exist
        if "navinnavi8431@gmail.com" not in registered:
            registered["navinnavi8431@gmail.com"] = {
                "id": "usr_navin_demo",
                "name": root_user.get("name", "Adarsh Sharma"),
                "email": "navinnavi8431@gmail.com",
                "password": "password123",
                "role": "student",
                "dob": "2002-05-15",
                "age": 24,
                "is_minor": False,
                "points": 450,
                "streak_days": 12,
                "daily_study_hours": 3.5,
                "focus_duration_minutes": 45,
                "college": "National Institute of Engineering",
                "grade_level": "3rd Year Computer Science (6th Sem)"
            }

        if "parent.suresh@gmail.com" not in registered:
            registered["parent.suresh@gmail.com"] = {
                "id": "usr_parent_suresh",
                "name": "Mr. Suresh Sharma",
                "email": "parent.suresh@gmail.com",
                "password": "password123",
                "role": "parent",
                "linked_student_email": "navinnavi8431@gmail.com"
            }

        for email, udata in registered.items():
            u_id = udata.get("id") or f"usr_{uuid.uuid4().hex[:12]}"
            pwd = udata.get("password", "password123")
            # Generate secure hash
            pwd_hash = generate_password_hash(pwd) if not pwd.startswith("scrypt:") and not pwd.startswith("pbkdf2:") else pwd
            
            self.execute("""
                INSERT OR IGNORE INTO users (
                    id, email, password_hash, name, role, dob, age, is_minor,
                    points, streak_days, daily_study_hours, focus_duration_minutes,
                    learning_preference, preferred_study_time, college, grade_level,
                    guardian_email, linking_code
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """ if self.engine_type == "sqlite" else """
                INSERT IGNORE INTO users (
                    id, email, password_hash, name, role, dob, age, is_minor,
                    points, streak_days, daily_study_hours, focus_duration_minutes,
                    learning_preference, preferred_study_time, college, grade_level,
                    guardian_email, linking_code
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                u_id,
                email.strip().lower(),
                pwd_hash,
                udata.get("name", "Student"),
                udata.get("role", "student"),
                udata.get("dob", ""),
                safe_int(udata.get("age"), 20),
                1 if udata.get("is_minor") else 0,
                safe_int(udata.get("points"), 100),
                safe_int(udata.get("streak_days"), 1),
                safe_float(udata.get("daily_study_hours"), 3.0),
                safe_int(udata.get("focus_duration_minutes"), 45),
                udata.get("learning_preference", "Practice problems and step-by-step review"),
                udata.get("preferred_study_time", "Evening"),
                udata.get("college", ""),
                udata.get("grade_level", ""),
                udata.get("guardian_email", ""),
                udata.get("linking_code", "TS-LINK-8921")
            ))

            # Student profile
            prof = udata.get("academic_profile") or data.get("academic_profile", {})
            self.execute("""
                INSERT OR IGNORE INTO student_profiles (
                    id, user_id, student_name, college, course, semester, specialization, academic_year
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """ if self.engine_type == "sqlite" else """
                INSERT IGNORE INTO student_profiles (
                    id, user_id, student_name, college, course, semester, specialization, academic_year
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                f"prof_{u_id}",
                u_id,
                udata.get("name", "Student"),
                prof.get("college") or udata.get("college", ""),
                prof.get("course") or "Computer Science & Engineering",
                prof.get("semester") or "Semester 6",
                prof.get("specialization") or "cs",
                prof.get("academic_year") or "2026-2027"
            ))

            # Subjects
            subj_list = udata.get("subjects") or data.get("subjects", [])
            for s in subj_list:
                s_id = s.get("id") or f"sub_{uuid.uuid4().hex[:8]}"
                self.execute("""
                    INSERT OR IGNORE INTO subjects (
                        id, user_id, name, code, credits, target_percentage, professor, room, color
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """ if self.engine_type == "sqlite" else """
                    INSERT IGNORE INTO subjects (
                        id, user_id, name, code, credits, target_percentage, professor, room, color
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    s_id, u_id, s.get("name", "Subject"), s.get("code", "CS101"),
                    safe_int(s.get("credits"), 3), safe_float(s.get("target_percentage"), 85.0),
                    s.get("professor", "Faculty"), s.get("room", "Room 402"),
                    s.get("color", "#3b82f6")
                ))

            # Classes
            class_list = udata.get("classes") or data.get("classes", [])
            for c in class_list:
                c_id = c.get("id") or f"cls_{uuid.uuid4().hex[:8]}"
                self.execute("""
                    INSERT OR IGNORE INTO classes (
                        id, user_id, subject_id, subject_name, day, time_slot, room, professor, color
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """ if self.engine_type == "sqlite" else """
                    INSERT IGNORE INTO classes (
                        id, user_id, subject_id, subject_name, day, time_slot, room, professor, color
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    c_id, u_id, c.get("subject_id", ""), c.get("subject_name", c.get("name", "Class")),
                    c.get("day", "Monday"), c.get("time_slot", c.get("time", "10:00 - 11:30 AM")),
                    c.get("room", "Room 402"), c.get("professor", c.get("faculty", "Professor")),
                    c.get("color", "#3b82f6")
                ))

            # Tasks
            task_list = udata.get("tasks") or data.get("tasks", [])
            for t in task_list:
                t_id = t.get("id") or f"tsk_{uuid.uuid4().hex[:8]}"
                self.execute("""
                    INSERT OR IGNORE INTO tasks (
                        id, user_id, subject_id, subject_name, title, description, due_date,
                        priority, status, points_reward, verified, verified_file, quiz_score, verified_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """ if self.engine_type == "sqlite" else """
                    INSERT IGNORE INTO tasks (
                        id, user_id, subject_id, subject_name, title, description, due_date,
                        priority, status, points_reward, verified, verified_file, quiz_score, verified_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    t_id, u_id, t.get("subject_id", ""), t.get("subject_name", t.get("subject", "Coursework")),
                    t.get("title", "Task"), t.get("description", ""), t.get("due_date", "Friday"),
                    t.get("priority", "medium"), t.get("status", "Pending"),
                    safe_int(t.get("points_reward", t.get("points")), 100),
                    1 if t.get("verified") else 0,
                    t.get("verified_file", ""),
                    t.get("quiz_score", ""),
                    t.get("verified_at", "")
                ))

            # Behavior patterns
            patterns = data.get("behavior_patterns", [])
            for p in patterns:
                p_id = p.get("id") or f"bp_{uuid.uuid4().hex[:8]}"
                self.execute("""
                    INSERT OR IGNORE INTO behavior_patterns (
                        id, user_id, title, pattern_type, confidence, evidence_count, evidence_summary, weight, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """ if self.engine_type == "sqlite" else """
                    INSERT IGNORE INTO behavior_patterns (
                        id, user_id, title, pattern_type, confidence, evidence_count, evidence_summary, weight, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    p_id, u_id, p.get("title", ""), p.get("pattern_type", "prioritization"),
                    safe_float(p.get("confidence"), 85.0), safe_int(p.get("evidence_count"), 5),
                    p.get("evidence_summary", ""), safe_float(p.get("weight"), 1.0),
                    1 if p.get("is_active", True) else 0
                ))

            # Exams
            exam_list = udata.get("exams") or data.get("exams", [])
            for ex in exam_list:
                ex_id = ex.get("id") or f"ex_{uuid.uuid4().hex[:8]}"
                self.execute("""
                    INSERT OR IGNORE INTO exams (
                        id, user_id, subject_id, subject_name, title, exam_date, weight_pct, target_score, syllabus_summary
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """ if self.engine_type == "sqlite" else """
                    INSERT IGNORE INTO exams (
                        id, user_id, subject_id, subject_name, title, exam_date, weight_pct, target_score, syllabus_summary
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    ex_id, u_id, ex.get("subject_id", ""), ex.get("subject_name", ex.get("subject", "Midterm")),
                    ex.get("title", "Exam"), ex.get("exam_date", ex.get("date", "2026-10-15")),
                    safe_float(ex.get("weight_pct", ex.get("weight", 30.0)), 30.0),
                    safe_float(ex.get("target_score", 85.0), 85.0),
                    ex.get("syllabus_summary", ex.get("syllabus", ""))
                ))

            # Grades
            grade_list = udata.get("grades") or data.get("grades", [])
            for gr in grade_list:
                gr_id = gr.get("id") or f"gr_{uuid.uuid4().hex[:8]}"
                self.execute("""
                    INSERT OR IGNORE INTO grades (
                        id, user_id, subject_id, subject_name, assessment_type, title, marks_obtained, max_marks, percentage, grade, term
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """ if self.engine_type == "sqlite" else """
                    INSERT IGNORE INTO grades (
                        id, user_id, subject_id, subject_name, assessment_type, title, marks_obtained, max_marks, percentage, grade, term
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    gr_id, u_id, gr.get("subject_id", ""), gr.get("subject_name", gr.get("subject", "Module")),
                    gr.get("assessment_type", gr.get("type", "Assignment")),
                    gr.get("title", "Test"),
                    safe_float(gr.get("marks_obtained", gr.get("score", 85.0)), 85.0),
                    safe_float(gr.get("max_marks", 100.0), 100.0),
                    safe_float(gr.get("percentage", 85.0), 85.0),
                    gr.get("grade", "A"),
                    gr.get("term", "Semester 6")
                ))

            # Decisions
            dec_list = data.get("decisions", []) or data.get("decision_history", [])
            for d_item in dec_list:
                d_id = d_item.get("id") or f"dec_{uuid.uuid4().hex[:8]}"
                self.execute("""
                    INSERT OR IGNORE INTO decisions (
                        id, user_id, question, baseline_data, simulation_result, recommended_option,
                        chosen_option, agreement, user_reason, outcome_rating, outcome_feedback
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """ if self.engine_type == "sqlite" else """
                    INSERT IGNORE INTO decisions (
                        id, user_id, question, baseline_data, simulation_result, recommended_option,
                        chosen_option, agreement, user_reason, outcome_rating, outcome_feedback
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    d_id, u_id, d_item.get("question", "Scenario"),
                    json.dumps(d_item.get("baseline_data", {})),
                    json.dumps(d_item.get("simulation_result", {})),
                    d_item.get("recommended_scenario") or d_item.get("recommended_option", "Option B"),
                    d_item.get("chosen_scenario") or d_item.get("chosen_option", "Option B"),
                    "disagree" if d_item.get("is_disagreement") else "agree",
                    d_item.get("user_reason", ""),
                    safe_int(d_item.get("outcome_rating"), 5),
                    d_item.get("outcome_feedback", "")
                ))

            # Permissions
            p_ctrl = udata.get("parent_controls") or data.get("parent_controls", {})
            self.execute("""
                INSERT OR IGNORE INTO permissions (
                    id, user_id, guardian_email, allow_view_study_hours, allow_view_proofs, allow_nudges, approved
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """ if self.engine_type == "sqlite" else """
                INSERT IGNORE INTO permissions (
                    id, user_id, guardian_email, allow_view_study_hours, allow_view_proofs, allow_nudges, approved
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                f"perm_{u_id}", u_id,
                p_ctrl.get("guardian_email", ""),
                1 if p_ctrl.get("allow_view_study_hours", True) else 0,
                1 if p_ctrl.get("allow_view_proofs", True) else 0,
                1 if p_ctrl.get("allow_nudges", True) else 0,
                1 if p_ctrl.get("guardian_approved", False) else 0
            ))

        print("[DB] Data migration completed successfully.")

    # ---------------- USER & SESSION METHODS ----------------
    def get_user_by_email(self, email: str):
        if not email:
            return None
        return self.fetchone("SELECT * FROM users WHERE LOWER(email) = LOWER(%s)", (email.strip(),))

    def get_user_by_id(self, user_id: str):
        if not user_id:
            return None
        return self.fetchone("SELECT * FROM users WHERE id = %s", (user_id,))

    def create_user(self, email: str, password: str, name: str, role="student", **kwargs):
        email_clean = email.strip().lower()
        existing = self.get_user_by_email(email_clean)
        if existing:
            return None, "An account with this email address already exists."

        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        password_hash = generate_password_hash(password)
        is_minor = 1 if kwargs.get("is_minor") else 0
        age = kwargs.get("age", 20)
        dob = kwargs.get("dob", "")
        guardian_email = kwargs.get("guardian_email", "")

        self.execute("""
            INSERT INTO users (
                id, email, password_hash, name, role, dob, age, is_minor, guardian_email
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, email_clean, password_hash, name, role, dob, age, is_minor, guardian_email))

        # Also create initial student_profile
        self.execute("""
            INSERT INTO student_profiles (id, user_id, student_name)
            VALUES (%s, %s, %s)
        """, (f"prof_{user_id}", user_id, name))

        user = self.get_user_by_id(user_id)
        return user, None

    def verify_user_login(self, identifier: str, password: str):
        user = self.get_user_by_email(identifier)
        if not user:
            # Check phone if matched
            user = self.fetchone("SELECT * FROM users WHERE linking_code = %s", (identifier,))
        if not user:
            return None, "No account found with this email address."

        stored_hash = user.get("password_hash", "")
        # Check hash, with legacy fallback
        if stored_hash.startswith("scrypt:") or stored_hash.startswith("pbkdf2:"):
            if not check_password_hash(stored_hash, password):
                return None, "Incorrect password. Please try again."
        else:
            # Plaintext fallback for legacy seeded passwords
            if stored_hash != password:
                return None, "Incorrect password. Please try again."
            # Rehash on successful plaintext login
            new_hash = generate_password_hash(password)
            self.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user["id"]))

        return user, None

    def create_session(self, user_id: str):
        token = f"tws_{uuid.uuid4().hex}_{int(datetime.datetime.now().timestamp())}"
        expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
        self.execute("""
            INSERT INTO sessions (token, user_id, expires_at)
            VALUES (%s, %s, %s)
        """, (token, user_id, expires_at.strftime("%Y-%m-%d %H:%M:%S")))
        return token

    def get_user_by_token(self, token: str):
        if not token:
            return None
        sess = self.fetchone("SELECT * FROM sessions WHERE token = %s", (token.strip(),))
        if not sess:
            return None
        return self.get_user_by_id(sess["user_id"])

    def delete_session(self, token: str):
        if token:
            self.execute("DELETE FROM sessions WHERE token = %s", (token.strip(),))

    # ---------------- USER-SCOPED DATA ACCESS & ACADEMIC STORAGE ----------------
    def save_user_academic_state(self, user_id: str, profile: dict, subjects: list, classes: list, tasks: list = None):
        if not user_id:
            return
        
        # 1. Update student profile
        p_name = profile.get("student_name") or ""
        p_college = profile.get("college") or ""
        p_course = profile.get("course") or ""
        p_semester = profile.get("semester") or ""
        p_spec = profile.get("specialization") or "cs"
        p_year = profile.get("academic_year") or "2026-2027"

        prof_exists = self.fetchone("SELECT id FROM student_profiles WHERE user_id = %s", (user_id,))
        if prof_exists:
            self.execute("""
                UPDATE student_profiles
                SET student_name = %s, college = %s, course = %s, semester = %s,
                    specialization = %s, academic_year = %s
                WHERE user_id = %s
            """, (p_name, p_college, p_course, p_semester, p_spec, p_year, user_id))
        else:
            p_id = f"prof_{uuid.uuid4().hex[:8]}"
            self.execute("""
                INSERT INTO student_profiles (id, user_id, student_name, college, course, semester, specialization, academic_year)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (p_id, user_id, p_name, p_college, p_course, p_semester, p_spec, p_year))

        # Update users table info
        grade_str = f"{p_course} ({p_semester})" if p_course and p_semester else (p_course or "")
        self.execute("""
            UPDATE users SET college = %s, grade_level = %s WHERE id = %s
        """, (p_college, grade_str, user_id))
        if p_name:
            self.execute("UPDATE users SET name = %s WHERE id = %s", (p_name, user_id))

        # 2. Update subjects
        self.execute("DELETE FROM subjects WHERE user_id = %s", (user_id,))
        for s in subjects:
            s_id = s.get("id") or f"s_{uuid.uuid4().hex[:10]}"
            s_name = s.get("name", "Subject")
            s_code = s.get("code", "")
            s_teacher = s.get("teacher") or s.get("professor") or "Faculty"
            s_room = s.get("room", "")
            s_credits = safe_int(s.get("credits"), 3)
            s_color = s.get("color", "#00C4CC")
            s_type = s.get("type", "Lecture")
            s_target = safe_float(s.get("target_percentage"), 85.0)

            self.execute("""
                INSERT INTO subjects (id, user_id, name, code, credits, target_percentage, professor, teacher, room, color, type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (s_id, user_id, s_name, s_code, s_credits, s_target, s_teacher, s_teacher, s_room, s_color, s_type))

        # 3. Update classes
        self.execute("DELETE FROM classes WHERE user_id = %s", (user_id,))
        for c in classes:
            c_id = c.get("id") or f"c_{uuid.uuid4().hex[:10]}"
            sub_id = c.get("subject_id", "")
            sub_name = c.get("subject") or c.get("subject_name") or "Class"
            c_day = c.get("day", "Monday")
            c_start = c.get("start_time", "10:00")
            c_end = c.get("end_time", "11:30")
            c_time = c.get("time") or f"{c_start} - {c_end}"
            c_teacher = c.get("teacher") or c.get("professor") or "Faculty"
            c_room = c.get("room", "")
            c_type = c.get("type", "Lecture")
            c_color = c.get("color", "#00C4CC")
            c_week = c.get("week_type", "All")

            self.execute("""
                INSERT INTO classes (id, user_id, subject_id, subject_name, subject, day, time_slot, time, start_time, end_time, room, professor, teacher, color, type, week_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (c_id, user_id, sub_id, sub_name, sub_name, c_day, c_time, c_time, c_start, c_end, c_room, c_teacher, c_teacher, c_color, c_type, c_week))

        # 4. Tasks (dynamic coursework tasks)
        if tasks is not None:
            self.execute("DELETE FROM tasks WHERE user_id = %s", (user_id,))
            for t in tasks:
                t_id = t.get("id") or f"t_{uuid.uuid4().hex[:10]}"
                self.execute("""
                    INSERT INTO tasks (id, user_id, subject_id, subject_name, title, description, due_date, priority, status, points_reward, verified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (t_id, user_id, t.get("subject_id", ""), t.get("subject", "Coursework"), t.get("title", ""), t.get("proof_required", ""), t.get("due_date", ""), t.get("priority", "High"), t.get("status", "Pending"), safe_int(t.get("points_reward", 100)), 1 if t.get("verified") else 0))

    def get_user_academic_state(self, user_id: str):
        user = self.get_user_by_id(user_id)
        if not user:
            return {}

        profile = self.fetchone("SELECT * FROM student_profiles WHERE user_id = %s", (user_id,))
        subjects = self.fetchall("SELECT * FROM subjects WHERE user_id = %s ORDER BY name ASC", (user_id,))
        classes = self.fetchall("SELECT * FROM classes WHERE user_id = %s ORDER BY day ASC, time_slot ASC", (user_id,))

        # Auto-sync existing subjects and classes from legacy JSON if relational DB is empty for this user
        if (len(subjects) == 0 or len(classes) == 0) and os.path.exists(LEGACY_JSON_PATH):
            try:
                with open(LEGACY_JSON_PATH, "r", encoding="utf-8") as f:
                    legacy_data = json.load(f)
                u_email = (user.get("email") or "").strip().lower()
                legacy_user = legacy_data.get("registered_users", {}).get(u_email)
                if not legacy_user and legacy_data.get("user", {}).get("email", "").lower() == u_email:
                    legacy_user = legacy_data.get("user", {})

                if legacy_user:
                    leg_subs = legacy_user.get("subjects") or legacy_data.get("subjects", [])
                    leg_cls = legacy_user.get("classes") or legacy_data.get("classes", [])
                    leg_prof = legacy_user.get("academic_profile") or legacy_data.get("academic_profile", {})
                    leg_tasks = legacy_user.get("tasks") or legacy_data.get("tasks", [])
                    if leg_subs or leg_cls:
                        self.save_user_academic_state(user_id, leg_prof, leg_subs, leg_cls, leg_tasks)
                        profile = self.fetchone("SELECT * FROM student_profiles WHERE user_id = %s", (user_id,))
                        subjects = self.fetchall("SELECT * FROM subjects WHERE user_id = %s ORDER BY name ASC", (user_id,))
                        classes = self.fetchall("SELECT * FROM classes WHERE user_id = %s ORDER BY day ASC, time_slot ASC", (user_id,))
            except Exception as e:
                print(f"[DB] Auto-sync from JSON notice: {e}")

        # Normalize subject fields for frontend
        for s in subjects:
            s["teacher"] = s.get("teacher") or s.get("professor") or "Faculty"
            s["professor"] = s["teacher"]
            s["type"] = s.get("type") or "Lecture"

        # Normalize class fields for frontend
        for c in classes:
            c["subject"] = c.get("subject") or c.get("subject_name") or "Class"
            c["subject_name"] = c["subject"]
            c["time"] = c.get("time") or c.get("time_slot") or ""
            c["time_slot"] = c["time"]
            c["teacher"] = c.get("teacher") or c.get("professor") or "Faculty"
            c["professor"] = c["teacher"]
            c["type"] = c.get("type") or "Lecture"
            c["week_type"] = c.get("week_type") or "All"
            c["start_time"] = c.get("start_time") or ""
            c["end_time"] = c.get("end_time") or ""

        tasks = self.fetchall("SELECT * FROM tasks WHERE user_id = %s ORDER BY status ASC, due_date ASC", (user_id,))
        for t in tasks:
            t["subject"] = t.get("subject_name") or t.get("subject") or "Coursework"
            t["subject_name"] = t["subject"]
            t["proof_status"] = "verified" if t.get("verified") else "pending"
            t["points"] = t.get("points_reward") or 100
            t["due"] = f"Due: {t.get('due_date')}" if t.get("due_date") else "Upcoming"

        exams = self.fetchall("SELECT * FROM exams WHERE user_id = %s ORDER BY exam_date ASC", (user_id,))
        grades = self.fetchall("SELECT * FROM grades WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        patterns = self.fetchall("SELECT * FROM behavior_patterns WHERE user_id = %s AND is_active = 1", (user_id,))
        permissions = self.fetchone("SELECT * FROM permissions WHERE user_id = %s", (user_id,))
        notifications = self.fetchall("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 20", (user_id,))

        return {
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "dob": user.get("dob", ""),
                "age": user.get("age", 20),
                "is_minor": bool(user.get("is_minor")),
                "role": user.get("role", "student"),
                "points": user.get("points", 100),
                "streak_days": user.get("streak_days", 1),
                "daily_study_hours": user.get("daily_study_hours", 3.0),
                "focus_duration_minutes": user.get("focus_duration_minutes", 45),
                "college": user.get("college", ""),
                "grade_level": user.get("grade_level", ""),
                "guardian_email": user.get("guardian_email", ""),
                "linking_code": user.get("linking_code", "TS-LINK-8921")
            },
            "academic_profile": profile or {},
            "subjects": subjects or [],
            "classes": classes or [],
            "tasks": tasks or [],
            "exams": exams or [],
            "grades": grades or [],
            "behavior_patterns": patterns or [],
            "parent_controls": permissions or {},
            "notifications": notifications or []
        }

    # ---------------- CHAT STORAGE ----------------
    def get_or_create_conversation(self, user_id: str, conv_id: str = None):
        if conv_id:
            conv = self.fetchone("SELECT * FROM chat_conversations WHERE id = %s AND user_id = %s", (conv_id, user_id))
            if conv:
                return conv["id"]
        
        # Check if user has an active conversation
        latest = self.fetchone("SELECT id FROM chat_conversations WHERE user_id = %s ORDER BY updated_at DESC LIMIT 1", (user_id,))
        if latest:
            return latest["id"]

        new_id = f"conv_{uuid.uuid4().hex[:12]}"
        self.execute("""
            INSERT INTO chat_conversations (id, user_id, title)
            VALUES (%s, %s, %s)
        """, (new_id, user_id, "Study Buddy Consultation"))
        return new_id

    def add_chat_message(self, conversation_id: str, user_id: str, role: str, content: str, context_used: str = None):
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        self.execute("""
            INSERT INTO chat_messages (id, conversation_id, user_id, role, content, context_used)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (msg_id, conversation_id, user_id, role, content, context_used))
        self.execute("""
            UPDATE chat_conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = %s
        """, (conversation_id,))
        return msg_id

    def get_recent_chat_messages(self, conversation_id: str, limit: int = 10):
        messages = self.fetchall("""
            SELECT role, content, created_at FROM chat_messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC LIMIT %s
        """, (conversation_id, limit))
        return messages

    # ---------------- DECISIONS & FEEDBACK ----------------
    def record_decision(self, user_id: str, question: str, baseline_data: dict, simulation_result: dict, recommended_option: str):
        dec_id = f"dec_{uuid.uuid4().hex[:12]}"
        self.execute("""
            INSERT INTO decisions (id, user_id, question, baseline_data, simulation_result, recommended_option)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            dec_id, user_id, question,
            json.dumps(baseline_data),
            json.dumps(simulation_result),
            recommended_option
        ))
        return dec_id

    def update_decision_feedback(self, decision_id: str, user_id: str, agreement: str, chosen_option: str, user_reason: str):
        self.execute("""
            UPDATE decisions
            SET agreement = %s, chosen_option = %s, user_reason = %s
            WHERE id = %s AND user_id = %s
        """, (agreement, chosen_option, user_reason, decision_id, user_id))

        # Calibrate behavior patterns based on feedback
        patterns = self.fetchall("SELECT * FROM behavior_patterns WHERE user_id = %s", (user_id,))
        for p in patterns:
            ev_count = p.get("evidence_count", 1) + 1
            cur_weight = p.get("weight", 1.0)
            if agreement == "agree":
                new_weight = min(2.0, cur_weight + 0.05)
                new_conf = min(98.0, p.get("confidence", 85.0) + 0.8)
            else:
                new_weight = max(0.5, cur_weight - 0.05)
                new_conf = max(60.0, p.get("confidence", 85.0) - 1.2)

            self.execute("""
                UPDATE behavior_patterns
                SET evidence_count = %s, weight = %s, confidence = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (ev_count, round(new_weight, 2), round(new_conf, 1), p["id"]))

        return True

# Global singleton instance
db_mgr = DatabaseManager()
