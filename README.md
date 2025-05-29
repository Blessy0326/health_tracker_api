# Health Record System

A Django REST API-based health record management system that allows patients to manage their health records and doctors to annotate them. The system includes JWT authentication, role-based permissions, and email notifications via Celery.

## Features

- **Patient Registration & Management**: Patients can register and manage their health records
- **Doctor Registration & Management**: Doctors can register and be assigned to patients
- **Health Records**: CRUD operations for patient health records
- **Annotations**: Doctors can add annotations to patient records
- **Assignment System**: Assign patients to doctors with email notifications
- **JWT Authentication**: Secure token-based authentication
- **Email Notifications**: Automated email notifications using Celery
- **Role-based Permissions**: Different access levels for patients and doctors

## Tech Stack

- **Backend**: Django 5.2, Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Task Queue**: Celery with Redis
- **Database**: SQLite (development) / PostgreSQL (production)
- **Email**: SMTP (Gmail configuration included)

## Prerequisites

### For Both Windows and Ubuntu
- Git
- Python 3.8 or higher
- Redis server (for Celery background tasks)

## Installation

### Windows Setup

#### 1. Install Python
- Download Python from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"
- Verify installation:
```cmd
python --version
pip --version
```

#### 2. Install Git
- Download Git from [git-scm.com](https://git-scm.com/download/win)
- Install with default settings

#### 3. Install Redis
**Option A: Using WSL2 (Recommended)**
```cmd
# Enable WSL2 and install Ubuntu
wsl --install
# After restart, in WSL2 terminal:
sudo apt update
sudo apt install redis-server
```

**Option B: Using Redis for Windows**
- Download Redis from [GitHub Releases](https://github.com/microsoftarchive/redis/releases)
- Extract and run `redis-server.exe`

### Ubuntu Setup

#### 1. Update System & Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv python3-dev git redis-server -y
```

#### 2. Start Redis Service
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
# Verify installation
redis-cli ping  # Should return: PONG
```

## Project Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/health_project.git
cd health_project
```

### 2. Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Ubuntu:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install django djangorestframework
pip install djangorestframework-simplejwt
pip install celery redis
pip install whitenoise
```

### 4. Configure Email Settings (Optional)
Update `health_project/settings.py` with your email credentials:

```python
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'  # Use App Password for Gmail
DEFAULT_FROM_EMAIL = 'your_email@gmail.com'
SERVER_EMAIL = 'your_email@gmail.com'
```

**For Gmail Setup:**
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password instead of your regular password

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional
python manage.py collectstatic --noinput
```

## Running the Application

You need to run **three services** simultaneously in separate terminals:

### Terminal 1: Start Redis Server

**Windows (Redis for Windows):**
```cmd
redis-server.exe
```

**Windows (WSL2):**
```cmd
# In WSL2 terminal:
sudo service redis-server start
```

**Ubuntu:**
```bash
sudo systemctl start redis-server
```

### Terminal 2: Start Django Development Server
```bash
# Activate virtual environment
source venv/bin/activate  # Ubuntu
# venv\Scripts\activate    # Windows

python manage.py runserver
```

Server will be available at: `http://127.0.0.1:8000/`

### Terminal 3: Start Celery Worker
```bash
# Activate virtual environment
source venv/bin/activate  # Ubuntu
# venv\Scripts\activate    # Windows

# Windows
celery -A health_project worker --loglevel=info --pool=solo

# Ubuntu
celery -A health_project worker --loglevel=info
```

### Optional: Start Celery Beat (for scheduled tasks)
```bash
# In another terminal with activated virtual environment
celery -A health_project beat --loglevel=info
```

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### User Registration
- `POST /api/register/patient/` - Register as patient
- `POST /api/register/doctor/` - Register as doctor

### User Management
- `GET /api/me/` - Get current user info
- `GET /api/my-assignments/` - Get user assignments

### Health Records
- `GET /api/health-records/` - List health records
- `POST /api/health-records/` - Create health record
- `GET /api/health-records/{id}/` - Get specific record
- `PUT /api/health-records/{id}/` - Update record
- `DELETE /api/health-records/{id}/` - Delete record

### Annotations
- `GET /api/annotations/` - List annotations
- `POST /api/annotations/` - Create annotation
- `GET /api/annotations/{id}/` - Get specific annotation
- `PUT /api/annotations/{id}/` - Update annotation
- `DELETE /api/annotations/{id}/` - Delete annotation

### Assignment Management
- `POST /api/assign-patient/` - Assign patient to doctor
- `GET /api/patient/{patient_id}/records/` - Get patient records (for assigned doctors)

## API Usage Examples

### 1. Register a Patient
```bash
curl -X POST http://127.0.0.1:8000/api/register/patient/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testpatient",
    "password": "testpass123",
    "confirm_password": "testpass123",
    "email": "patient@example.com",
    "first_name": "Test",
    "last_name": "Patient"
  }'
```

### 2. Register a Doctor
```bash
curl -X POST http://127.0.0.1:8000/api/register/doctor/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testdoctor",
    "password": "testpass123",
    "confirm_password": "testpass123",
    "email": "doctor@example.com",
    "first_name": "Test",
    "last_name": "Doctor",
    "medical_license": "MD123456"
  }'
```

### 3. Get JWT Token
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testpatient",
    "password": "testpass123"
  }'
```

### 4. Create Health Record (with JWT token)
```bash
curl -X POST http://127.0.0.1:8000/api/health-records/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Annual Checkup",
    "content": "Regular health checkup completed. All vitals normal."
  }'
```

### 5. Assign Patient to Doctor
```bash
curl -X POST http://127.0.0.1:8000/api/assign-patient/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "doctor_id": 2,
    "patient_id": 1
  }'
```

## User Roles & Permissions

### Patient Permissions
- Register and manage own account
- Create, read, update, delete own health records
- View own assignments (assigned doctors)

### Doctor Permissions  
- Register and manage own account
- View health records of assigned patients only
- Create, read, update, delete annotations on assigned patients' records
- View own assignments (assigned patients)

## Development Commands

### Django Commands
```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Django shell
python manage.py shell

# Check for issues
python manage.py check
```

### Celery Commands
```bash
# Start worker
celery -A health_project worker --loglevel=info

# Start beat scheduler
celery -A health_project beat --loglevel=info

# Monitor tasks (requires: pip install flower)
celery -A health_project flower
```

## Troubleshooting

### Common Issues

#### 1. Redis Connection Error
- Ensure Redis server is running: `redis-cli ping` should return `PONG`
- Check if port 6379 is available
- For Windows, try using WSL2 for Redis

#### 2. Email Not Sending
- Verify email credentials in `settings.py`
- For Gmail, use App Password instead of regular password
- Check Django logs for specific errors
- Ensure Celery worker is running

#### 3. Permission Errors (Ubuntu)
```bash
sudo chown -R $USER:$USER /path/to/project
```

#### 4. Port Already in Use
```bash
# Use different port
python manage.py runserver 8001
```

#### 5. Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # Ubuntu
# venv\Scripts\activate   # Windows
```

### Debugging Commands
```bash
# Django detailed logs
python manage.py runserver --verbosity=2

# Celery debug logs
celery -A health_project worker --loglevel=debug

# Redis logs (Ubuntu)
sudo journalctl -u redis-server

# Check Redis status
redis-cli info
```

## Production Deployment

### Environment Variables
Create a `.env` file for sensitive data:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=your-database-url
```

### Security Settings
Update `settings.py` for production:
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'localhost']
SECRET_KEY = os.environ.get('SECRET_KEY')

# Use PostgreSQL for production
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}
```

## Testing the Application

### Access Points
- Django Admin: `http://127.0.0.1:8000/admin/`
- API Root: `http://127.0.0.1:8000/api/`
- Health Records: `http://127.0.0.1:8000/api/health-records/`
- Annotations: `http://127.0.0.1:8000/api/annotations/`

### Test Workflow
1. Register a patient and doctor
2. Obtain JWT tokens for both users
3. Create health records as patient
4. Assign patient to doctor
5. Add annotations as doctor
6. Verify email notifications (if configured)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and commit: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Django and Celery documentation
3. Create an issue in the GitHub repository