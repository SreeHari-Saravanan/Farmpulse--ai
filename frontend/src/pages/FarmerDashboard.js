import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import api from '../services/api';
import toast from 'react-hot-toast';

const FarmerDashboard = () => {
  const { user, logout } = useAuth();
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showReportForm, setShowReportForm] = useState(false);
  
  // Form state
  const [symptomText, setSymptomText] = useState('');
  const [images, setImages] = useState([]);
  const [cropType, setCropType] = useState('');

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      const response = await api.get('/reports/');
      setReports(response.data);
    } catch (error) {
      toast.error('Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReport = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('text_symptoms', symptomText);
    formData.append('crop_type', cropType);
    images.forEach((image) => {
      formData.append('images', image);
    });

    try {
      await api.post('/reports/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      toast.success('Report created successfully!');
      setShowReportForm(false);
      setSymptomText('');
      setImages([]);
      setCropType('');
      loadReports();
    } catch (error) {
      toast.error('Failed to create report');
    }
  };

  const handleImageChange = (e) => {
    setImages(Array.from(e.target.files));
  };

  const handleConnectVet = async (reportId) => {
    try {
      // Create a video session
      const response = await api.post('/signaling/session/create', {
        report_id: reportId,
        farmer_id: user.id,
        vet_id: null // Will be assigned when vet joins
      });
      
      const sessionId = response.data.session_id;
      
      // Navigate to video call page with session ID
      navigate(`/video-call?session=${sessionId}&report=${reportId}`);
      
      toast.success('Connecting to veterinarian...');
    } catch (error) {
      console.error('Failed to create session:', error);
      toast.error('Failed to connect. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">FarmPulse AI</h1>
          <div className="flex items-center space-x-4">
            <select
              value={i18n.language}
              onChange={(e) => i18n.changeLanguage(e.target.value)}
              className="border rounded px-2 py-1"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी</option>
              <option value="ta">தமிழ்</option>
            </select>
            <span className="text-gray-600">{user?.full_name}</span>
            <button onClick={logout} className="text-red-600 hover:text-red-800">
              {t('logout')}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Actions */}
        <div className="mb-6">
          <button
            onClick={() => setShowReportForm(!showReportForm)}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-medium"
          >
            {showReportForm ? 'Cancel' : t('newReport')}
          </button>
        </div>

        {/* Report Form */}
        {showReportForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Create New Report</h2>
            <form onSubmit={handleCreateReport} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Describe Symptoms *
                </label>
                <textarea
                  value={symptomText}
                  onChange={(e) => setSymptomText(e.target.value)}
                  required
                  rows="4"
                  className="w-full border border-gray-300 rounded-md p-2"
                  placeholder="Describe what you're observing..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Images (optional)
                </label>
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleImageChange}
                  className="w-full border border-gray-300 rounded-md p-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Crop/Animal Type
                </label>
                <input
                  type="text"
                  value={cropType}
                  onChange={(e) => setCropType(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                  placeholder="e.g., Tomato, Wheat, Cattle"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700"
              >
                {t('submit')}
              </button>
            </form>
          </div>
        )}

        {/* Reports List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h2 className="text-xl font-bold">{t('myReports')}</h2>
          </div>
          
          {loading ? (
            <div className="p-6 text-center">{t('loading')}</div>
          ) : reports.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No reports yet. Create your first report!
            </div>
          ) : (
            <div className="divide-y">
              {reports.map((report) => (
                <div key={report.id} className="p-6 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className={`px-3 py-1 text-xs rounded-full ${
                          report.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          report.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {report.status}
                        </span>
                        <span className={`px-3 py-1 text-xs rounded-full ${
                          report.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                          report.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {report.priority}
                        </span>
                      </div>
                      
                      <p className="text-gray-600 mb-2">
                        {report.symptoms?.text?.substring(0, 100)}...
                      </p>
                      
                      {report.ai_prediction && (
                        <div className="bg-blue-50 p-3 rounded mt-2">
                          <p className="font-medium text-blue-900">
                            AI Prediction: {report.ai_prediction.disease_label}
                          </p>
                          <p className="text-sm text-blue-700">
                            Confidence: {(report.ai_prediction.confidence * 100).toFixed(1)}%
                          </p>
                        </div>
                      )}
                      
                      {report.diagnosis && (
                        <div className="bg-green-50 p-3 rounded mt-2">
                          <p className="font-medium text-green-900">
                            Vet Diagnosis: {report.diagnosis}
                          </p>
                          {report.treatment && (
                            <p className="text-sm text-green-700 mt-1">
                              {report.treatment}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                    
                    <div className="ml-4 space-y-2">
                      {report.status === 'pending' && (
                        <button 
                          onClick={() => handleConnectVet(report.id)}
                          className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700"
                        >
                          Connect with Vet
                        </button>
                      )}
                      {report.pdf_url && (
                        <a 
                          href={report.pdf_url}
                          download
                          className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 block text-center"
                        >
                          Download PDF
                        </a>
                      )}
                    </div>
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    Created: {new Date(report.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default FarmerDashboard;
