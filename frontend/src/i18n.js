import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Translation resources
const resources = {
  en: {
    translation: {
      // Common
      "welcome": "Welcome to FarmPulse AI",
      "login": "Login",
      "signup": "Sign Up",
      "logout": "Logout",
      "submit": "Submit",
      "cancel": "Cancel",
      "save": "Save",
      "delete": "Delete",
      "edit": "Edit",
      "loading": "Loading...",
      
      // Roles
      "farmer": "Farmer",
      "vet": "Veterinarian",
      "admin": "Administrator",
      
      // Dashboard
      "dashboard": "Dashboard",
      "myReports": "My Reports",
      "newReport": "New Report",
      "caseQueue": "Case Queue",
      "analytics": "Analytics",
      
      // Reports
      "symptoms": "Symptoms",
      "diagnosis": "Diagnosis",
      "treatment": "Treatment",
      "prescription": "Prescription",
      "aiPrediction": "AI Prediction",
      "confidence": "Confidence",
      "status": "Status",
      "priority": "Priority",
      
      // Status
      "pending": "Pending",
      "inProgress": "In Progress",
      "completed": "Completed",
      "closed": "Closed",
      
      // Actions
      "connectWithVet": "Connect with Veterinarian",
      "startVideoCall": "Start Video Call",
      "downloadPDF": "Download PDF",
      "viewDetails": "View Details",
      
      // Alerts
      "outbreakAlert": "Outbreak Alert",
      "diseaseDetected": "Disease Detected",
      "checkYourAnimals": "Please check your animals/crops"
    }
  },
  hi: {
    translation: {
      "welcome": "फार्मपल्स एआई में आपका स्वागत है",
      "login": "लॉगिन",
      "signup": "साइन अप करें",
      "logout": "लॉग आउट",
      "submit": "जमा करें",
      "cancel": "रद्द करें",
      "farmer": "किसान",
      "vet": "पशु चिकित्सक",
      "dashboard": "डैशबोर्ड",
      "symptoms": "लक्षण",
      "diagnosis": "निदान",
      "treatment": "उपचार",
      "aiPrediction": "एआई भविष्यवाणी",
      "outbreakAlert": "प्रकोप चेतावनी"
    }
  },
  ta: {
    translation: {
      "welcome": "FarmPulse AI க்கு வரவேற்கிறோம்",
      "login": "உள்நுழைக",
      "signup": "பதிவு செய்க",
      "farmer": "விவசாயி",
      "vet": "கால்நடை மருத்துவர்",
      "symptoms": "அறிகுறிகள்",
      "diagnosis": "நோய் கண்டறிதல்"
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
