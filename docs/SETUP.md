# ARCS Setup Guide

Complete setup instructions for the AI-Driven Ransomware Detection & Containment System.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- MongoDB Atlas account
- Supabase account

## Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/arcs-ransomware-detection.git
cd arcs-ransomware-detection
```

### 2. Configure Environment Variables

#### Backend Configuration
```bash
cd backend
cp .env.example .env
# Edit .env with your MongoDB URI and other settings
```

#### Frontend Configuration
```bash
cd frontend
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 3. Start Infrastructure Services
```bash
# Start Kafka and Zookeeper
docker-compose up -d
```

### 4. Start Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend will run on http://localhost:8000

### 5. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend will run on http://localhost:3000

### 6. Create Admin User in Supabase

Run the SQL in `create_admin_user.sql` in your Supabase SQL Editor to create the admin user.

## Detailed Configuration

### MongoDB Atlas Setup
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get connection string
4. Add to `backend/.env` as `MONGODB_URI`

### Supabase Setup
1. Create account at https://supabase.com
2. Create new project
3. Get URL and anon key from Settings → API
4. Add to `frontend/.env`
5. Run `create_admin_user.sql` in SQL Editor

### RBAC Configuration
- Admin user: Set in Supabase user metadata
- See `RBAC_SETUP.md` for detailed role configuration

## Testing

### Test Backend
```bash
cd backend
python test_api.py
```

### Test Kafka
```bash
python test_kafka_send.py
```

### Run Simulation
```bash
cd simulation
python ransomware_simulator.py
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### MongoDB Connection Failed
- Check MongoDB Atlas IP whitelist
- Verify connection string format
- Ensure network access is configured

### Supabase Authentication Issues
- Verify API keys are correct
- Check user exists in Supabase dashboard
- Ensure email is confirmed

## Next Steps

- Read `API_DOCUMENTATION.md` for API reference
- Check `FEATURES.md` for feature list
- See `TESTING.md` for testing guide
- Review `ARCHITECTURE.md` for system design

## Support

For issues, please open a GitHub issue with:
- Error message
- Steps to reproduce
- Your environment details
