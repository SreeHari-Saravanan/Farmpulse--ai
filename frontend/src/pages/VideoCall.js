import React, { useEffect, useRef, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

/**
 * WebRTC Video Call Component
 * 
 * Implements peer-to-peer video calling using WebRTC with FastAPI WebSocket signaling
 * 
 * Flow:
 * 1. Connect to signaling WebSocket
 * 2. Create RTCPeerConnection
 * 3. Get local media stream
 * 4. Exchange SDP offer/answer via WebSocket
 * 5. Exchange ICE candidates
 * 6. Establish direct P2P connection
 */

const VideoCall = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session');
  const reportId = searchParams.get('report');
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [localStream, setLocalStream] = useState(null);
  const [remoteStream, setRemoteStream] = useState(null);
  const [callStatus, setCallStatus] = useState('Connecting...');
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const peerConnection = useRef(null);
  const signalingSocket = useRef(null);

  const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
  const role = user?.role === 'farmer' ? 'farmer' : 'vet';

  useEffect(() => {
    initializeCall();

    return () => {
      cleanup();
    };
  }, []);

  const initializeCall = async () => {
    try {
      // Get local media stream
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      
      setLocalStream(stream);
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }

      // Initialize peer connection with the stream
      initPeerConnection(stream);
      
      // Connect to signaling server
      connectSignaling();
      
      setCallStatus('Waiting for peer...');
    } catch (error) {
      console.error('Failed to initialize call:', error);
      toast.error('Failed to access camera/microphone');
      setCallStatus('Error');
    }
  };

  const initPeerConnection = (stream) => {
    // STUN servers for NAT traversal
    const configuration = {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
      ]
    };

    peerConnection.current = new RTCPeerConnection(configuration);

    // Add local stream tracks to peer connection
    stream.getTracks().forEach(track => {
      peerConnection.current.addTrack(track, stream);
      console.log('Added local track:', track.kind);
    });

    // Handle remote stream
    peerConnection.current.ontrack = (event) => {
      console.log('Received remote track');
      setRemoteStream(event.streams[0]);
      if (remoteVideoRef.current) {
        remoteVideoRef.current.srcObject = event.streams[0];
      }
      setCallStatus('Connected');
    };

    // Handle ICE candidates
    peerConnection.current.onicecandidate = (event) => {
      if (event.candidate && signalingSocket.current?.readyState === WebSocket.OPEN) {
        signalingSocket.current.send(JSON.stringify({
          type: 'ice-candidate',
          candidate: event.candidate
        }));
      }
    };

    // Connection state change
    peerConnection.current.onconnectionstatechange = () => {
      console.log('Connection state:', peerConnection.current.connectionState);
      if (peerConnection.current.connectionState === 'connected') {
        setCallStatus('Connected');
      } else if (peerConnection.current.connectionState === 'disconnected') {
        setCallStatus('Disconnected');
      }
    };
  };

  const connectSignaling = () => {
    const wsUrl = `${WS_URL}/ws/signaling/${sessionId}/${user.id}/${role}`;
    signalingSocket.current = new WebSocket(wsUrl);

    signalingSocket.current.onopen = () => {
      console.log('Signaling connected');
      
      // Send ready signal to let peer know we're connected
      signalingSocket.current.send(JSON.stringify({
        type: 'ready',
        role: role
      }));
      
      // If farmer, create and send offer
      if (role === 'farmer') {
        setTimeout(() => createOffer(), 500); // Small delay to ensure vet is ready
      }
    };

    signalingSocket.current.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      console.log('Received signaling message:', data.type);
      
      switch (data.type) {
        case 'ready':
          // Peer is ready - if we're farmer, send offer
          if (role === 'farmer') {
            console.log('Peer ready, creating offer...');
            createOffer();
          }
          break;
        case 'offer':
          console.log('Received offer');
          await handleOffer(data.sdp);
          break;
        case 'answer':
          console.log('Received answer');
          await handleAnswer(data.sdp);
          break;
        case 'ice-candidate':
          await handleIceCandidate(data.candidate);
          break;
        case 'hangup':
          handleRemoteHangup();
          break;
        case 'peer-disconnected':
          setCallStatus('Peer disconnected');
          break;
        default:
          break;
      }
    };

    signalingSocket.current.onerror = (error) => {
      console.error('Signaling error:', error);
      toast.error('Signaling connection error');
    };

    signalingSocket.current.onclose = () => {
      console.log('Signaling disconnected');
    };
  };

  const createOffer = async () => {
    try {
      console.log('Creating offer...');
      const offer = await peerConnection.current.createOffer({
        offerToReceiveAudio: true,
        offerToReceiveVideo: true
      });
      await peerConnection.current.setLocalDescription(offer);
      
      console.log('Sending offer');
      signalingSocket.current.send(JSON.stringify({
        type: 'offer',
        sdp: offer
      }));
    } catch (error) {
      console.error('Error creating offer:', error);
    }
  };

  const handleOffer = async (offer) => {
    try {
      console.log('Setting remote description from offer');
      await peerConnection.current.setRemoteDescription(new RTCSessionDescription(offer));
      
      console.log('Creating answer');
      const answer = await peerConnection.current.createAnswer();
      await peerConnection.current.setLocalDescription(answer);
      
      console.log('Sending answer');
      signalingSocket.current.send(JSON.stringify({
        type: 'answer',
        sdp: answer
      }));
    } catch (error) {
      console.error('Error handling offer:', error);
    }
  };

  const handleAnswer = async (answer) => {
    try {
      await peerConnection.current.setRemoteDescription(new RTCSessionDescription(answer));
    } catch (error) {
      console.error('Error handling answer:', error);
    }
  };

  const handleIceCandidate = async (candidate) => {
    try {
      await peerConnection.current.addIceCandidate(new RTCIceCandidate(candidate));
    } catch (error) {
      console.error('Error adding ICE candidate:', error);
    }
  };

  const handleRemoteHangup = () => {
    toast.info('Remote user ended the call');
    cleanup();
    navigate(-1);
  };

  const toggleMute = () => {
    if (localStream) {
      localStream.getAudioTracks().forEach(track => {
        track.enabled = !track.enabled;
      });
      setIsMuted(!isMuted);
    }
  };

  const toggleVideo = () => {
    if (localStream) {
      localStream.getVideoTracks().forEach(track => {
        track.enabled = !track.enabled;
      });
      setIsVideoOff(!isVideoOff);
    }
  };

  const endCall = () => {
    if (signalingSocket.current?.readyState === WebSocket.OPEN) {
      signalingSocket.current.send(JSON.stringify({ type: 'hangup' }));
    }
    cleanup();
    navigate(-1);
  };

  const cleanup = () => {
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
    }
    if (peerConnection.current) {
      peerConnection.current.close();
    }
    if (signalingSocket.current) {
      signalingSocket.current.close();
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 px-6 py-4 flex justify-between items-center">
        <div className="text-white">
          <h2 className="text-xl font-bold">Video Consultation</h2>
          <p className="text-sm text-gray-400">{callStatus}</p>
        </div>
        <button
          onClick={endCall}
          className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg"
        >
          End Call
        </button>
      </div>

      {/* Video Container */}
      <div className="flex-1 relative p-4">
        {/* Remote Video (main) */}
        <div className="absolute inset-4 bg-black rounded-lg overflow-hidden">
          {remoteStream ? (
            <video
              ref={remoteVideoRef}
              autoPlay
              playsInline
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="flex items-center justify-center h-full text-white">
              <div className="text-center">
                <div className="text-6xl mb-4">👤</div>
                <p>Waiting for remote video...</p>
              </div>
            </div>
          )}
        </div>

        {/* Local Video (picture-in-picture) */}
        <div className="absolute bottom-8 right-8 w-64 h-48 bg-black rounded-lg overflow-hidden shadow-lg border-2 border-gray-700">
          <video
            ref={localVideoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover mirror"
          />
          <div className="absolute bottom-2 left-2 text-white text-sm bg-black bg-opacity-50 px-2 py-1 rounded">
            You
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-gray-800 px-6 py-4 flex justify-center space-x-4">
        <button
          onClick={toggleMute}
          className={`p-4 rounded-full ${isMuted ? 'bg-red-600' : 'bg-gray-700'} hover:bg-opacity-80`}
        >
          <span className="text-white text-xl">{isMuted ? '🔇' : '🎤'}</span>
        </button>
        
        <button
          onClick={toggleVideo}
          className={`p-4 rounded-full ${isVideoOff ? 'bg-red-600' : 'bg-gray-700'} hover:bg-opacity-80`}
        >
          <span className="text-white text-xl">{isVideoOff ? '📹' : '🎥'}</span>
        </button>
      </div>

      <style jsx>{`
        .mirror {
          transform: scaleX(-1);
        }
      `}</style>
    </div>
  );
};

export default VideoCall;
