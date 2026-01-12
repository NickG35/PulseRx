# PulseRx

A comprehensive pharmacy management system with real-time notifications, medication reminders, and inventory tracking. Built as a portfolio project to demonstrate full-stack Django development with WebSocket integration and background task processing.

## Features

### Patient Portal
- **Medication Reminders**: Schedule reminders with customizable frequencies and times
- **Smart Suggestions**: AI-powered dosage and timing recommendations based on medication type
- **Prescription Refills**: Request refills with real-time status tracking
- **Pharmacy Management**: View and change pharmacy affiliations
- **Real-time Notifications**: Instant updates via WebSocket for messages and prescription status

### Pharmacist Dashboard
- **Prescription Management**: Create, approve, and track patient prescriptions
- **Refill Processing**: Handle patient refill requests with inventory validation
- **Inventory Tracking**: Monitor medication stock levels and resupply status
- **Resupply Requests**: Request inventory replenishment from administrators
- **Messaging System**: Direct communication with patients and administrators

### Administrator Panel
- **Multi-Pharmacy Management**: Oversee multiple pharmacy locations
- **Inventory Control**: Approve resupply requests and manage stock across pharmacies
- **Drug Database**: Import and manage medication database with dosage recommendations
- **User Management**: Handle pharmacist and patient accounts
- **System-wide Notifications**: Broadcast updates to all users

## Tech Stack

### Backend
- **Django 5.0**: Web framework
- **Django Channels**: WebSocket support for real-time features
- **Celery**: Background task processing for scheduled reminders
- **Redis**: Message broker for Celery and Channels
- **PostgreSQL**: Production database (SQLite for development)

### Frontend
- **DaisyUI + TailwindCSS**: Modern UI components and styling
- **JavaScript (Vanilla)**: Dynamic form interactions and WebSocket handling
- **Font Awesome**: Icon library

### Deployment
- **Render.com**: Platform-as-a-Service hosting
- **Daphne**: ASGI server for WebSocket support
- **WhiteNoise**: Static file serving
- **Gunicorn**: WSGI server (fallback)

## Local Development Setup

### Prerequisites
- Python 3.11+
- Redis Server
- Node.js and npm (for TailwindCSS)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd PulseRx
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Install TailwindCSS**
```bash
npm install
```

5. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your local settings (optional for development)
```

6. **Database setup**
```bash
python manage.py migrate
python manage.py createsuperuser
```

7. **Import drug database (optional)**
```bash
python manage.py import_drugs pharmacy/data/drugs.csv
```

8. **Seed demo data (for testing)**
```bash
./seed_demo.sh
# Or view available accounts:
python show_demo_accounts.py
# See DEMO-SCENARIOS.md for testing workflows
```

### Running the Application (4 Terminal Setup)

**Terminal 1: Django Development Server**
```bash
source venv/bin/activate
python manage.py runserver
# Or use Daphne for WebSocket support:
daphne -b 0.0.0.0 -p 8000 PulseRx.asgi:application
```

**Terminal 2: Celery Worker (for reminders)**
```bash
./start-services.sh
# Or manually:
source venv/bin/activate
redis-server &
celery -A PulseRx worker --loglevel=info
```

**Terminal 3: TailwindCSS Watch**
```bash
npm run dev
# Watches for CSS changes and rebuilds
```

**Terminal 4: Optional - Celery Beat (scheduled tasks)**
```bash
source venv/bin/activate
celery -A PulseRx beat --loglevel=info
```

Access the application at `http://localhost:8000`

## Deployment to Render

### 1. Create Render Account
Sign up at [render.com](https://render.com)

### 2. Create PostgreSQL Database
- Click "New +" → "PostgreSQL"
- Name: `pulserx-db`
- Copy the **Internal Database URL** for later

### 3. Create Redis Instance
- Click "New +" → "Redis"
- Name: `pulserx-redis`
- Copy the **Internal Redis URL** for later

### 4. Create Web Service
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Configure:
  - **Name**: `pulserx`
  - **Build Command**: `./build.sh`
  - **Start Command**: `daphne -b 0.0.0.0 -p $PORT PulseRx.asgi:application`

### 5. Environment Variables
Add these in Render dashboard under "Environment":

```env
SECRET_KEY=<generate-secure-random-string>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
DATABASE_URL=<internal-database-url-from-step-2>
REDIS_URL=<internal-redis-url-from-step-3>
PYTHON_VERSION=3.11.0
```

### 6. Create Background Worker (for Celery)
- Click "New +" → "Background Worker"
- Use same repository
- **Start Command**: `celery -A PulseRx worker --loglevel=info`
- Add same environment variables as web service

### 7. Deploy
- Render will automatically deploy on push to main branch
- Monitor build logs for any issues
- Run migrations if needed (build.sh handles this)

## Project Structure

```
PulseRx/
├── accounts/           # User authentication, messaging, notifications
│   ├── consumers.py   # WebSocket consumers
│   ├── models.py      # User, Message, Thread, Notifications
│   └── views.py       # Account management, messaging
├── patients/          # Patient portal functionality
│   ├── models.py      # MedicationReminder, ReminderTime
│   ├── views.py       # Reminder CRUD, refill requests
│   └── templates/     # Patient UI templates
├── pharmacy/          # Pharmacy and admin functionality
│   ├── models.py      # Prescription, Drug, Pharmacy
│   ├── views.py       # Prescription management, inventory
│   └── templates/     # Pharmacy UI templates
├── PulseRx/          # Project settings
│   ├── settings.py   # Django configuration
│   ├── asgi.py       # ASGI application (WebSockets)
│   └── celery.py     # Celery configuration
├── static/           # CSS, JavaScript, images
├── templates/        # Base templates
├── build.sh          # Render deployment script
├── requirements.txt  # Python dependencies
└── manage.py         # Django CLI
```

## Key Features Implementation

### Real-time Notifications
WebSocket consumers in [accounts/consumers.py](accounts/consumers.py) handle:
- Message notifications with unread counts
- Prescription status updates
- Inventory alerts
- Auto-marking messages as read when thread is open

### Medication Reminders
Celery tasks scheduled via [patients/views.py](patients/views.py):
- Dynamic time input generation based on frequency
- Dosage and timing suggestions
- Task cancellation on reminder deletion
- Duplicate time validation

### Inventory Management
Multi-pharmacy inventory tracking in [pharmacy/views.py](pharmacy/views.py):
- Stock level monitoring
- Resupply request workflow (Pharmacist → Admin)
- Automatic notifications to all pharmacists in pharmacy

## Security Features

- Custom password validators (uppercase, lowercase, number requirements)
- CSRF protection enabled
- SQL injection prevention via Django ORM
- XSS protection with template auto-escaping
- Role-based access control (Patient/Pharmacist/Admin)
- Environment variable configuration for secrets

## Troubleshooting

### Reminders not triggering
- Ensure Celery worker is running: `ps aux | grep celery`
- Check Redis is running: `redis-cli ping` (should return PONG)
- Verify CELERY_BROKER_URL in settings matches Redis URL

### WebSocket notifications not working
- Use Daphne instead of runserver: `daphne -b 0.0.0.0 -p 8000 PulseRx.asgi:application`
- Check CHANNEL_LAYERS configuration points to Redis
- Verify WebSocket connection in browser console

### Static files not loading on Render
- Run `python manage.py collectstatic` (build.sh does this)
- Check STATIC_ROOT and STATICFILES_STORAGE settings
- Verify WhiteNoise middleware is in MIDDLEWARE list

### Database migrations failing
- Ensure DATABASE_URL environment variable is set
- Check PostgreSQL credentials are correct
- Run migrations manually: `python manage.py migrate`

## Demo Data & Testing

### Quick Demo Setup
```bash
# Seed comprehensive demo data with various scenarios
./seed_demo.sh

# View all demo accounts and credentials
python show_demo_accounts.py
```

### What's Included
The demo data seeder creates realistic scenarios for testing:
- **Inventory**: Out of stock, low stock, and in-stock items with resupply flags
- **Prescriptions**: Active prescriptions, refill requests, expiring prescriptions
- **Reminders**: Active reminders, archived reminders, reminders running out
- **Messages**: Patient-pharmacist conversations with read/unread states
- **Notifications**: Various notification types with read/unread states

See [DEMO-SCENARIOS.md](DEMO-SCENARIOS.md) for detailed testing workflows and [DEMO-DATA-GUIDE.md](DEMO-DATA-GUIDE.md) for complete data descriptions.

### Multi-Role Testing
To test multiple roles simultaneously in the same browser:
1. **Regular Window**: Login as Pharmacist
2. **Incognito Window**: Login as Patient
3. **Another Browser Profile**: Login as Admin

This allows you to see real-time interactions between different user types.

## Development Notes

### Adding New Features
- Always test with all three user roles (Patient/Pharmacist/Admin)
- Validate edge cases (negative refills, duplicate times, cascade deletions)
- Use `send_notification_with_counts()` for WebSocket notifications
- Cancel Celery tasks on model deletion to prevent orphaned tasks

### TailwindCSS Changes
- Edit classes in templates
- TailwindCSS watch will auto-rebuild: `npm run dev`
- For production: `npm run build`

## Contributing

This is a portfolio project, but suggestions and feedback are welcome!

## License

MIT License - feel free to use this project as a reference for your own work.

## Author

Built as a portfolio demonstration of full-stack Django development with real-time features.

---

**Live Demo**: [Your Render URL]
**Portfolio**: [Your Portfolio Link]
**Contact**: [Your Contact Info]
