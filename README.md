# 🚀 Academic ERP System with Controlled Workflow Architecture

A role-based Academic ERP system designed to enforce **real-world academic workflows**, ensuring **data integrity, role separation, and controlled processing** of critical operations like grading.

---

## 📸 System Preview

<!-- Add 2-3 screenshots here -->
<!-- Example:
![Dashboard](images/dashboard.png)
![Grades](images/grades.png)
-->

---

## 🎯 Core Concept

Most academic ERP projects focus on UI and CRUD operations.

This system is built around a stricter principle:

> **No single role should have complete control over critical academic data.**

It introduces a **multi-step workflow system** where responsibilities are distributed and validated.

---

## 🔐 Core Features

- **Single Authentication System**
  - Role-based login (Student / Faculty / Admin / Exam Section)
  - Session-based authentication

- **Role-Based Access Control (RBAC)**
  - Strict permission enforcement per role
  - Protected operations and restricted data access

- **Security**
  - Password hashing
  - CSRF protection
  - Controlled access to critical data

---

## 🎓 Student Module

- View **attendance with shortage indicators**
- Access **SGPA & CGPA (read-only)**
- Track assignments with submission status
- View timetable, notifications, and academic calendar
- Participate in **doubts forum (Q&A system)**

> Students have **visibility, not control** over academic data.

---

## 👨‍🏫 Faculty Module

- Submit marks using **structured templates**
- Manage attendance (controlled updates)
- Create and evaluate assignments
- Answer and moderate student doubts

> Faculty act as **data contributors**, not final authorities.

---

## 🛠️ Admin Module

- Manage users (students & faculty)
- Define academic structure (courses, subjects, timetables)
- Publish announcements, events, and holidays
- Control system-level configurations

> Admin defines the **system boundaries and structure**.

---

## 📊 Key Feature: Controlled Grade Processing Pipeline

This system enforces a **multi-step evaluation workflow** instead of direct grade entry.

### 🔄 Workflow
Faculty → Upload Marks
↓
Exam Section → Verify & Process
↓
System → Compute SGPA/CGPA
↓
Student → View Final Results


### Key Properties:
- No direct grade manipulation by faculty  
- Centralized computation ensures consistency  
- Separation of responsibilities across roles  

> **No single role has end-to-end control over grades.**

---

## 💡 Design Principles

- Separation of responsibilities across roles  
- Data integrity over convenience  
- Workflow-driven system design  
- Interconnected modules (not isolated features)  

---

## 🧰 Tech Stack

- **Backend:** Django  
- **Frontend:** HTML, CSS, JavaScript (Bootstrap)  
- **Database:** SQLite / PostgreSQL  
- **Authentication:** Django Authentication System  

---

## 🚀 Getting Started

```bash
git clone https://github.com/DeepikaReddy0607/college-erp-system.git
cd your-repo

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
