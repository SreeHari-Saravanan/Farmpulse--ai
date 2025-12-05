import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import api from '../services/api';
import toast from 'react-hot-toast';

const VetDashboard = () => {
  const { user, logout } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ status: '', priority: '' });
  const [activeSessions, setActiveSessions] = useState([]);
  const [wsConnection, setWsConnection] = useState(null);

  // Update form
  const [vetNotes, setVetNotes] = useState('');
  const [diagnosis, setDiagnosis] = useState('');
  const [treatment, setTreatment] = useState('');

  useEffect(() => {
    loadReports();
    loadActiveSessions();
    connectWebSocket();

    return () => {
      if (wsConnection) {
        wsConnection.close();
      }
    };
  }, [filters]);

  const connectWebSocket = () => {
    const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    const ws = new WebSocket(`${WS_URL}/ws/${user.id}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'new_session') {
        toast((t) => (
          <div>
            <p className="font-bold">New Video Call Request!</p>
            <p className="text-sm">A farmer is requesting a consultation</p>
            <button
              onClick={() => {
                toast.dismiss(t.id);
                joinCall(data.session_id, data.report_id);
              }}
              className="mt-2 bg-green-600 text-white px-4 py-2 rounded text-sm"
            >
              Join Call
            </button>
          </div>
        ), { duration: 30000 });
        
        loadActiveSessions();
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };

    setWsConnection(ws);
  };

  const loadActiveSessions = async () => {
    try {
      const response = await api.get('/signaling/sessions/active');
      setActiveSessions(response.data || []);
    } catch (error) {
      console.error('Failed to load active sessions:', error);
    }
  };

  const joinCall = async (sessionId, reportId) => {
    try {
      // Update session with vet_id
      await api.patch(`/signaling/session/${sessionId}/join`, {
        vet_id: user.id
      });

      // Navigate to video call
      navigate(`/video-call?session=${sessionId}&report=${reportId}`);
      toast.success('Joining call...');
    } catch (error) {
      console.error('Failed to join call:', error);
      toast.error('Failed to join call');
    }
  };

  const loadReports = async () => {
    try {
      const params = {};
      if (filters.status) params.status_filter = filters.status;
      if (filters.priority) params.priority_filter = filters.priority;
      
      const response = await api.get('/reports/', { params });
      setReports(response.data);
    } catch (error) {
      toast.error('Failed to load cases');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectReport = async (reportId) => {
    try {
      const response = await api.get(`/reports/${reportId}`);
      setSelectedReport(response.data);
      setVetNotes(response.data.vet_notes || '');
      setDiagnosis(response.data.diagnosis || response.data.ai_prediction?.disease_label || '');
      setTreatment(response.data.treatment || '');
    } catch (error) {
      toast.error('Failed to load report details');
    }
  };

  const handleUpdateReport = async () => {
    if (!selectedReport) return;

    try {
      await api.patch(`/reports/${selectedReport.id}`, {
        status: 'in_progress',
        vet_notes: vetNotes,
        diagnosis: diagnosis,
        treatment: treatment,
        final_disease_label: diagnosis
      });
      
      toast.success('Report updated successfully');
      loadReports();
      setSelectedReport(null);
    } catch (error) {
      toast.error('Failed to update report');
    }
  };

  const handleCloseCase = async () => {
    if (!selectedReport) return;

    try {
      await api.patch(`/reports/${selectedReport.id}`, {
        status: 'completed',
        vet_notes: vetNotes,
        diagnosis: diagnosis,
        treatment: treatment,
        prescription: `Prescription for ${diagnosis}: ${treatment}`,
        final_disease_label: diagnosis
      });
      
      toast.success('Case closed successfully');
      loadReports();
      setSelectedReport(null);
    } catch (error) {
      toast.error('Failed to close case');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Veterinarian Dashboard</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">Dr. {user?.full_name}</span>
            <button onClick={logout} className="text-red-600 hover:text-red-800">
              {t('logout')}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Active Call Sessions */}
        {activeSessions.length > 0 && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-bold text-green-900 mb-3">Active Call Requests</h3>
            <div className="space-y-2">
              {activeSessions.map((session) => (
                <div key={session.id} className="bg-white rounded p-3 flex justify-between items-center">
                  <div>
                    <p className="font-medium">Report #{session.report_id?.slice(-6)}</p>
                    <p className="text-sm text-gray-600">
                      Waiting for {Math.floor((new Date() - new Date(session.call_start)) / 1000)}s
                    </p>
                  </div>
                  <button
                    onClick={() => joinCall(session.id, session.report_id)}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                  >
                    Join Call
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Case Queue */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="px-4 py-3 border-b">
                <h2 className="text-lg font-bold">Case Queue</h2>
                
                {/* Filters */}
                <div className="mt-3 space-y-2">
                  <select
                    value={filters.status}
                    onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                    className="w-full border rounded px-2 py-1 text-sm"
                  >
                    <option value="">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                  </select>
                  
                  <select
                    value={filters.priority}
                    onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                    className="w-full border rounded px-2 py-1 text-sm"
                  >
                    <option value="">All Priority</option>
                    <option value="urgent">Urgent</option>
                    <option value="high">High</option>
                    <option value="normal">Normal</option>
                  </select>
                </div>
              </div>

              <div className="divide-y max-h-[600px] overflow-y-auto">
                {loading ? (
                  <div className="p-4 text-center text-sm text-gray-500">Loading...</div>
                ) : reports.length === 0 ? (
                  <div className="p-4 text-center text-sm text-gray-500">No cases</div>
                ) : (
                  reports.map((report) => (
                    <div
                      key={report.id}
                      onClick={() => handleSelectReport(report.id)}
                      className={`p-4 cursor-pointer hover:bg-gray-50 ${
                        selectedReport?.id === report.id ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          report.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                          report.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {report.priority}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(report.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      
                      <p className="text-sm font-medium text-gray-900 mb-1">
                        {report.farmer_name || 'Farmer'}
                      </p>
                      
                      <p className="text-xs text-gray-600 line-clamp-2">
                        {report.symptoms?.text}
                      </p>
                      
                      {report.ai_prediction && (
                        <p className="text-xs text-blue-600 mt-1 font-medium">
                          AI: {report.ai_prediction.disease_label}
                        </p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Case Details */}
          <div className="lg:col-span-2">
            {!selectedReport ? (
              <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                Select a case from the queue to view details
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold mb-4">Case Details</h2>
                
                {/* Patient Info */}
                <div className="bg-gray-50 p-4 rounded mb-4">
                  <h3 className="font-medium mb-2">Patient Information</h3>
                  <p className="text-sm"><strong>Farmer:</strong> {selectedReport.farmer_name}</p>
                  <p className="text-sm"><strong>Type:</strong> {selectedReport.crop_type || selectedReport.animal_type || 'Not specified'}</p>
                  <p className="text-sm"><strong>Created:</strong> {new Date(selectedReport.created_at).toLocaleString()}</p>
                </div>

                {/* Symptoms */}
                <div className="mb-4">
                  <h3 className="font-medium mb-2">Reported Symptoms</h3>
                  <p className="text-sm text-gray-700">{selectedReport.symptoms?.text}</p>
                  {selectedReport.symptoms?.images?.length > 0 && (
                    <div className="mt-2 flex space-x-2">
                      {selectedReport.symptoms.images.map((img, idx) => (
                        <img
                          key={idx}
                          src={img}
                          alt="symptom"
                          className="w-24 h-24 object-cover rounded border"
                        />
                      ))}
                    </div>
                  )}
                </div>

                {/* AI Prediction */}
                {selectedReport.ai_prediction && (
                  <div className="bg-blue-50 p-4 rounded mb-4">
                    <h3 className="font-medium mb-2">AI Analysis</h3>
                    <p className="text-sm"><strong>Prediction:</strong> {selectedReport.ai_prediction.disease_label}</p>
                    <p className="text-sm"><strong>Confidence:</strong> {(selectedReport.ai_prediction.confidence * 100).toFixed(1)}%</p>
                    {selectedReport.ai_prediction.explanation && (
                      <p className="text-sm mt-1 text-gray-600">{selectedReport.ai_prediction.explanation}</p>
                    )}
                  </div>
                )}

                {/* Vet Input */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Your Notes
                    </label>
                    <textarea
                      value={vetNotes}
                      onChange={(e) => setVetNotes(e.target.value)}
                      rows="3"
                      className="w-full border border-gray-300 rounded-md p-2 text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Final Diagnosis
                    </label>
                    <input
                      type="text"
                      value={diagnosis}
                      onChange={(e) => setDiagnosis(e.target.value)}
                      className="w-full border border-gray-300 rounded-md p-2 text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Treatment Plan
                    </label>
                    <textarea
                      value={treatment}
                      onChange={(e) => setTreatment(e.target.value)}
                      rows="4"
                      className="w-full border border-gray-300 rounded-md p-2 text-sm"
                    />
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={handleUpdateReport}
                      className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
                    >
                      Update Case
                    </button>
                    <button
                      onClick={handleCloseCase}
                      className="flex-1 bg-green-600 text-white py-2 rounded hover:bg-green-700"
                    >
                      Close & Save Prescription
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default VetDashboard;
