# 🚀 FarmPulse AI - Quick Start Guide

## ✅ Setup Complete!

Your FarmPulse AI platform is now fully set up and running!

---

## 🌐 Access the Application

### Frontend (React)
- **URL:** http://localhost:3000
- **Status:** ✅ Running

### Backend API (FastAPI)
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Status:** ✅ Running

---

## 👤 Test Credentials

### Farmer Account
- **Email:** `farmer@test.com`
- **Password:** `farmer123`
- **Role:** Create reports, upload images, view AI predictions, video consultation

### Veterinarian Account
- **Email:** `vet@test.com`
- **Password:** `vet123`
- **Role:** Review cases, provide diagnoses, override AI predictions, video calls

### Admin Account
- **Email:** `admin@test.com`
- **Password:** `admin123`
- **Role:** View analytics, manage users, export reports, system monitoring

---

## 🎯 Key Features Working

### ✅ Authentication
- JWT-based auth with secure password hashing
- Role-based access control (farmer/vet/admin)
- Token management and session handling

### ✅ Disease Reporting
- Text symptom description
- Image upload (supports multiple formats)
- Location tagging (geospatial indexing)
- AI-powered analysis (mock predictions ready)

### ✅ AI Analysis Pipeline
- Hybrid NLP + Computer Vision fusion
- Disease prediction with confidence scores
- Treatment recommendations
- Similar case search
- Feedback loop for continuous improvement

### ✅ Veterinarian Workflow
- Case queue with filtering
- Real-time notifications (Redis pub/sub)
- Case assignment and status management
- AI prediction override with feedback logging

### ✅ Video Consultation
- WebRTC peer-to-peer video calls
- WebSocket-based signaling server
- Session management and metadata tracking
- Ready for TURN server integration

### ✅ Admin Dashboard
- User management
- System analytics
- Health monitoring
- Report export (CSV/JSON/PDF ready)
- Geospatial heatmaps

### ✅ Offline Support
- Service worker structure ready
- IndexedDB storage patterns
- Sync queue for offline operations

### ✅ Internationalization
- Multi-language support (English, Hindi, Tamil)
- Easy to add more languages
- RTL support ready

### ✅ Real-time Features
- WebSocket notifications
- Live case updates
- Outbreak alerts

---

## 🗄️ Database

### Sample Data Seeded
- ✅ 3 users (farmer, vet, admin)
- ✅ 15 sample disease reports (various statuses)
- ✅ 1 completed video session
- ✅ 3 feedback entries
- ✅ Geospatial indexes for location-based queries
- ✅ Text indexes for search functionality

### MongoDB Collections
- `users` - User accounts with roles
- `reports` - Disease reports with AI predictions
- `sessions` - Video consultation sessions
- `feedback` - AI prediction feedback for model improvement
- `notifications` - In-app notifications

---

## 🛠️ Development Commands

### Start Servers (Quick)
```powershell
.\start_servers.ps1
```
This opens two PowerShell windows:
- Backend server on http://localhost:8000
- Frontend dev server on http://localhost:3000

### Manual Start - Backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Manual Start - Frontend
```powershell
cd frontend
npm start
```

### Re-seed Database
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python .\scripts\seed_db.py
```

### Run Tests
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest
```

---

## 📡 API Testing

### Using Postman
1. Import collection: `tests/FarmPulse_Postman_Collection.json`
2. Set base URL: `http://localhost:8000`
3. Run workflows:
   - Auth → Create Report → AI Analysis
   - Vet Review → Status Update
   - WebRTC Signaling Flow

### Using cURL (PowerShell)
```powershell
# Health Check
curl http://localhost:8000/health

# Login
$response = curl http://localhost:8000/api/auth/login -Method POST -ContentType "application/json" -Body '{"email":"farmer@test.com","password":"farmer123"}'
$token = ($response.Content | ConvertFrom-Json).access_token

# Get Reports
curl http://localhost:8000/api/reports/ -Headers @{"Authorization"="Bearer $token"}

# Create Report
curl http://localhost:8000/api/reports/ -Method POST -Headers @{"Authorization"="Bearer $token"} -ContentType "application/json" -Body '{"animal_type":"cow","symptoms":"Coughing and fever","location":{"type":"Point","coordinates":[-122.4194,37.7749]}}'
```

---

## 🔧 Configuration

### Backend (.env)
Located: `backend/.env`
```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=farmpulse

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Redis
REDIS_URL=redis://localhost:6379

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]
```

### Frontend (.env)
Located: `frontend/.env`
```bash
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

---

## 🚀 Production Deployment Checklist

### Security
- [ ] Change `JWT_SECRET_KEY` to a strong random value (min 32 chars)
- [ ] Set `ENVIRONMENT=production` in backend/.env
- [ ] Enable HTTPS for all endpoints
- [ ] Configure proper CORS origins
- [ ] Set up API rate limiting
- [ ] Enable Redis password authentication
- [ ] Use MongoDB with authentication enabled

### AI Models
- [ ] Replace mock models in `backend/models/` with real trained models
- [ ] Set up TensorFlow/PyTorch serving
- [ ] Configure model versioning
- [ ] Set up A/B testing for model improvements

### External Services
- [ ] Configure Google Cloud Translation API
- [ ] Set up Google Speech-to-Text
- [ ] Add Twilio credentials for SMS
- [ ] Configure SMTP for email notifications
- [ ] Set up Agora/Twilio for production video calls
- [ ] Configure TURN servers for WebRTC

### Infrastructure
- [ ] Set up MongoDB replica set
- [ ] Configure Redis cluster/sentinel
- [ ] Set up CDN for static assets
- [ ] Configure load balancer
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure logging aggregation (ELK stack)
- [ ] Set up automated backups

### Frontend
- [ ] Run `npm run build` for optimized production build
- [ ] Configure service worker for offline support
- [ ] Set up CDN for static assets
- [ ] Enable gzip/brotli compression
- [ ] Configure CSP headers

---

## 📊 System Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  React Frontend │◄───────►│  FastAPI Backend│
│  (Port 3000)    │  HTTP   │  (Port 8000)    │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │ WebSocket                 │
         │                           │
         └───────────────────────────┤
                                     │
         ┌───────────────────────────┼────────────────┐
         │                           │                │
    ┌────▼─────┐              ┌─────▼────┐    ┌─────▼─────┐
    │ MongoDB  │              │  Redis   │    │  AI Models│
    │ (27017)  │              │  (6379)  │    │  (Mock)   │
    └──────────┘              └──────────┘    └───────────┘
```

---

## 🐛 Troubleshooting

### Backend won't start
```powershell
# Check MongoDB is running
mongosh

# Check Redis is running
redis-cli ping

# Check Python packages
cd backend
.\venv\Scripts\Activate.ps1
pip list
```

### Frontend build errors
```powershell
cd frontend
Remove-Item -Recurse node_modules
Remove-Item package-lock.json
npm install
```

### Database issues
```powershell
# Drop database and reseed
mongosh
use farmpulse
db.dropDatabase()
exit

# Then reseed
cd backend
.\venv\Scripts\Activate.ps1
python .\scripts\seed_db.py
```

### Port already in use
```powershell
# Find process using port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess

# Kill process (replace PID)
Stop-Process -Id PID -Force
```

---

## 📚 Documentation

- **Implementation Guide:** `docs/IMPLEMENTATION_GUIDE.md`
- **Project Summary:** `docs/PROJECT_SUMMARY.md`
- **API Documentation:** http://localhost:8000/docs (when running)
- **Postman Collection:** `tests/FarmPulse_Postman_Collection.json`

---

## 🎉 Next Steps

### For Farmers
1. Visit http://localhost:3000
2. Login with `farmer@test.com` / `farmer123`
3. Click "Create New Report"
4. Describe symptoms or upload images
5. Get instant AI predictions
6. Schedule video call with vet if needed

### For Vets
1. Login with `vet@test.com` / `vet123`
2. View pending cases in queue
3. Review AI predictions and farmer inputs
4. Provide diagnosis and treatment plan
5. Join video calls with farmers
6. Override AI predictions when needed (helps improve model)

### For Admins
1. Login with `admin@test.com` / `admin123`
2. Monitor system health and analytics
3. View user activity and report trends
4. Export data for analysis
5. View geospatial disease heatmap

### For Developers
1. Explore API at http://localhost:8000/docs
2. Review code in `backend/app/` and `frontend/src/`
3. Run Postman collection for workflow testing
4. Check logs in terminal for debugging
5. Integrate real AI models in `backend/app/services/ai_inference.py`
6. Add more languages in `frontend/src/i18n.js`

---

## 🤝 Support & Contribution

### Found a bug?
- Check logs in backend terminal
- Review browser console (F12)
- Check MongoDB/Redis connectivity

### Want to add features?
- Follow existing code patterns
- Update API docs in docstrings
- Add tests for new endpoints
- Update Postman collection

---

## ✨ Success! Your FarmPulse AI Platform is Live!

**Farmers can now report diseases, get AI predictions, and connect with vets.**
**Veterinarians can review cases and provide expert diagnoses.**
**Admins can monitor the system and track disease outbreaks.**

🌾 Happy farming! 🚜
