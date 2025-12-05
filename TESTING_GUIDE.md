# FarmPulse AI - Testing Guide

## 🚀 Quick Start

Both servers should now be running:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 👤 Test Credentials

| Role   | Email              | Password   |
|--------|-------------------|------------|
| Farmer | farmer@test.com   | farmer123  |
| Vet    | vet@test.com      | vet123     |
| Admin  | admin@test.com    | admin123   |

## ✅ Manual Testing Checklist

### 1. Authentication Flow
- [ ] Open http://localhost:3000
- [ ] Should redirect to login page
- [ ] Try logging in with **farmer@test.com / farmer123**
- [ ] Should successfully log in and redirect to Farmer Dashboard
- [ ] Refresh the page - should stay logged in
- [ ] Click logout - should return to login page

### 2. Farmer Dashboard
Login as farmer and test:
- [ ] View existing reports (should see ~15 sample reports)
- [ ] Create new report:
  - Fill in animal/crop type
  - Add symptoms description
  - Upload an image (optional - any image file)
  - Submit
- [ ] View AI predictions on reports
- [ ] Check that location is shown on reports

### 3. Vet Dashboard
Login as vet (logout first, then login with vet@test.com):
- [ ] View pending cases queue
- [ ] Click on a case to see details
- [ ] Update diagnosis/treatment recommendations
- [ ] Change status to "in_progress" or "completed"
- [ ] Verify that override feedback is logged

### 4. Admin Dashboard
Login as admin:
- [ ] View analytics summary (total reports, users, etc.)
- [ ] See reports by status breakdown
- [ ] View users list
- [ ] Export reports (downloads CSV)
- [ ] View geo-heatmap data

### 5. Video Call (WebRTC)
- [ ] From Farmer Dashboard, click "Start Video Call"
- [ ] Allow camera/microphone permissions
- [ ] Should see local video stream
- [ ] Test mute/unmute audio
- [ ] Test start/stop video
- [ ] End call

*Note: For full P2P video testing, you need two users in separate browsers/devices*

### 6. Language Switching (i18n)
- [ ] Look for language selector (if implemented in UI)
- [ ] Switch between English, Hindi, Tamil
- [ ] Verify that UI text changes

### 7. Offline Functionality
- [ ] Create a report while online
- [ ] Open browser DevTools → Network tab
- [ ] Set to "Offline" mode
- [ ] Try to view existing data (should work from cache)
- [ ] Go back online
- [ ] Verify sync works

## 🔧 API Testing with Postman

1. Import the collection: `tests/FarmPulse_Postman_Collection.json`
2. Set the base URL to `http://localhost:8000/api`
3. Run the collection to test all endpoints

### Key Endpoints to Test:

#### Authentication
```bash
POST /api/auth/signup
POST /api/auth/login
GET  /api/auth/me (with Bearer token)
```

#### Reports
```bash
POST /api/reports/          # Create report
GET  /api/reports/          # List all reports
GET  /api/reports/{id}      # Get specific report
PUT  /api/reports/{id}      # Update report (vet only)
```

#### AI Analysis
```bash
POST /api/ai/analyze-text   # Text-based symptom analysis
POST /api/ai/analyze-image  # Image-based diagnosis
GET  /api/ai/similar-cases  # Find similar cases (vet only)
```

#### Admin
```bash
GET /api/admin/health       # Health check
GET /api/admin/analytics    # System analytics
GET /api/admin/users        # List all users
GET /api/admin/reports      # Export reports
```

#### WebSocket Signaling
```bash
POST /api/signaling/session/create    # Create video session
POST /api/signaling/session/{id}/end  # End session
```

## 🐛 Known Issues / TODOs

### Currently Using Mocks:
- ✅ AI Models (returns mock predictions)
- ✅ Google Translate API (uses mock translation)
- ✅ Google Speech-to-Text (uses mock transcription)
- ✅ SMS Service (logs instead of sending)
- ✅ Email Service (logs instead of sending)

### To Enable Real Services:
1. **AI Models**: Place trained models in `backend/models/` and update `ai_inference.py`
2. **Google Cloud**: Add API keys to `.env` file
3. **Twilio SMS**: Add Twilio credentials to `.env`
4. **SMTP Email**: Add email server credentials to `.env`
5. **TURN Server**: Add TURN server config for production WebRTC

## 📊 Database Verification

Check MongoDB data:
```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/farmpulse

# View collections
show collections

# Count documents
db.users.countDocuments()      # Should be 3
db.reports.countDocuments()    # Should be ~15
db.sessions.countDocuments()   # Should be 1
db.feedback.countDocuments()   # Should be 3

# View a user
db.users.findOne({ email: "farmer@test.com" })

# View reports
db.reports.find().limit(2).pretty()
```

## 🔍 Debugging Tips

### Backend Issues:
- Check logs in the backend terminal
- Visit http://localhost:8000/docs for interactive API docs
- Check MongoDB connection: http://localhost:8000/api/admin/health
- View Redis data: `redis-cli` → `KEYS *`

### Frontend Issues:
- Open browser DevTools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for failed API calls
- Check Application → Local Storage for stored token

### Common Fixes:
- **CORS errors**: Check backend CORS_ORIGINS in .env
- **401 Unauthorized**: Check if token is being sent in headers
- **404 Not Found**: Verify API endpoint paths
- **Connection refused**: Ensure MongoDB and Redis are running

## 📈 Performance Testing

Test with sample load:
```bash
# Use Apache Bench or similar tool
ab -n 1000 -c 10 http://localhost:8000/api/admin/health
```

## 🎯 Next Steps

1. **Replace Mocks**: Integrate real AI models and external services
2. **Add Tests**: Write unit tests for backend (pytest) and frontend (Jest)
3. **Security**: Add rate limiting, input validation, SQL injection protection
4. **Monitoring**: Set up logging aggregation (ELK stack) and monitoring (Prometheus)
5. **Deployment**: Containerize with Docker and deploy to cloud (AWS/GCP/Azure)
6. **CI/CD**: Set up GitHub Actions for automated testing and deployment

---

## 💡 Tips for Development

- Keep both terminal windows visible to monitor logs
- Use the API docs at http://localhost:8000/docs for quick testing
- Check the implementation guide: `docs/IMPLEMENTATION_GUIDE.md`
- Review the project summary: `docs/PROJECT_SUMMARY.md`

Happy Testing! 🎉
