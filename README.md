# United Staffing AI Bench Platform

A production-grade AI-powered Bench Sales Operating System for US IT staffing organizations.

The platform centralizes consultant management, vendor management, requirements, submissions, AI-powered matching, communications, tasks, analytics, and recruiter workflows into a single platform.

---

## Overview

United Staffing AI Bench Platform is designed to replace manual spreadsheets and fragmented recruiter workflows with a centralized web-based platform.

The system provides role-based access, consultant and vendor management, requirement tracking, candidate submissions, AI-assisted matching, workflow management, communications, reporting, and operational analytics.

---

## Core Modules

### Authentication & Authorization
- JWT-based authentication
- Role-based access control
- Secure password hashing
- Authentication session management
- Protected frontend routes
- Admin bootstrap support

### Consultant Management
- Consultant profiles
- Visa and work authorization information
- Skills and technologies
- Rate information
- Consultant status tracking
- Consultant search and filtering

### Vendor Management
- Vendor management
- Vendor contacts
- Vendor-related requirement workflows
- Vendor service operations

### Requirements Management
- Create and manage requirements
- Requirement status tracking
- Technology and skill associations
- Requirement history
- Requirement documents
- Filtering and pagination

### Submission Management
- Consultant submissions
- Submission status tracking
- Submission history
- Submission service workflows
- Requirement-to-consultant submission tracking

### AI Matching
- AI-assisted consultant matching
- Technology and skill matching
- Matching history
- Match scoring and ranking logic

### Communications
- Communication records
- Recruiter communication workflows
- Communication tracking

### Tasks & Workflow
- Recruiter task management
- Task assignment
- Task status tracking
- Workflow rules
- Workflow execution tracking
- Daily recruiter workflow support

### Marketing
- Consultant marketing activity tracking
- Marketing history

### Analytics & Reporting
- Dashboard analytics
- Executive analytics
- Vendor dashboard analytics
- Report definitions
- Report execution tracking

### Integrations
- Integration connection management
- Integration synchronization state tracking

### Audit & Notifications
- Audit records
- Notifications
- Business event tracking

---

## Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router

### Backend

- Python
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic / Pydantic Settings
- Async PostgreSQL access

### Database

- PostgreSQL

### Authentication

- JWT
- Argon2 password hashing
- Role-based authorization

### Infrastructure

- Docker
- Docker Compose
- Nginx
- GitHub

---

## Architecture

                    ┌──────────────────────┐
                    │      React UI        │
                    │  TypeScript + Vite   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       Nginx          │
                    │   Frontend Gateway   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │      REST API        │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
          ┌──────────┐   ┌───────────┐  ┌────────────┐
          │ Services │   │ SQLAlchemy│  │  Security  │
          │ & Logic  │   │    ORM    │  │ JWT/Auth   │
          └──────────┘   └─────┬─────┘  └────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     PostgreSQL       │
                    └──────────────────────┘

---

## Project Structure

```text
United-Staffing-AI-Bench-Platform/
│
├── backend/
│   ├── src/
│   │   └── app/
│   │       ├── ai_matching/
│   │       ├── analytics/
│   │       ├── audit/
│   │       ├── auth/
│   │       ├── automation/
│   │       ├── communications/
│   │       ├── consultants/
│   │       ├── integrations/
│   │       ├── marketing/
│   │       ├── matching/
│   │       ├── notifications/
│   │       ├── planner/
│   │       ├── reporting/
│   │       ├── requirements/
│   │       ├── submissions/
│   │       ├── tasks/
│   │       └── vendors/
│   │
│   ├── tests/
│   ├── migrations/
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── .github/
│   └── workflows/
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── Makefile
└── README.md
```

---

## Developmentcls

### Prerequisites

 - Docker Desktop
 - Git
 - Node.js (for frontend development when running outside Docker)
 - Python 3.x (for backend development when running outside Docker)

## Start the Development Environment

```bash
docker compose up --build
```

## Stop the Development Environment

```bash
docker compose down
```

The application services are managed through Docker Compose.

---

## Production Configuration

A production Docker Compose configuration is included:

```bash
docker compose -f docker-compose.prod.yml up --build
```

The production configuration includes:

 - PostgreSQL
 - FastAPI backend
 - React frontend
 - Nginx
 - Container health dependency handling
 - Production frontend API configuration

---

## Testing

The backend includes a comprehensive automated test suite covering:

 - Authentication
 - Core application behavior
 - Consultants
 - Vendors
 - Requirements
 - Submissions
 - AI matching
 - Communications
 - Integrations
 - Middleware
 - Exception handling
 - Application startup

Run backend tests with:


```bash
pytest
```

---

## Environment Configuration

Create a local .env file from the example configuration:

```bash
cp .env.example .env
```

Windows PowerShell:

```bash
Copy-Item .env.example .env
```

Never commit .env or other files containing secrets to Git.

---

## Security

The project includes:

 - JWT authentication
 - Argon2 password hashing
 - Role-based authorization
 - Protected API routes
 - Protected frontend routes
 - Security response headers
 - Environment-based secret configuration
 - Git ignore rules for local secrets and runtime data

---

## Project Status

### Completed

 - Backend foundation
 - Frontend foundation
 - Authentication
 - Authorization
 - Dashboard
 - Consultant CRM
 - Vendor management
 - Requirements management
 - Submission management
 - AI matching
 - Communications
 - Tasks and workflow management
 - Marketing activity tracking
 - Analytics and reporting
 - Integrations
 - Notifications
 - Audit functionality
 - Automated testing
 - Production Docker configuration
 - Frontend Nginx configuration
 - Git repository cleanup

The current repository represents the completed development scope of the platform.

---

## Repository

This repository is maintained as a private project for United Staffing Associates.

## License

Private Project

United Staffing Associates