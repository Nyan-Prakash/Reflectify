// frontend/src/components/AudioRecorder.jsx
import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

function AudioRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [status, setStatus] = useState("Ready to record");
  const [error, setError] = useState(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [audioDevices, setAudioDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioPreview, setAudioPreview] = useState(null);
  
  const chunksRef = useRef([]);
  const audioStreamRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const timerRef = useRef(null);

  // Get available audio devices
  useEffect(() => {
    const getAudioDevices = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = devices.filter(device => device.kind === 'audioinput');
        setAudioDevices(audioInputs);
        if (audioInputs.length > 0) {
          setSelectedDevice(audioInputs[0].deviceId);
        }
      } catch (err) {
        console.error('Error getting audio devices:', err);
      }
    };

    getAudioDevices();
  }, []);

  // Timer for recording duration
  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      clearInterval(timerRef.current);
      setRecordingTime(0);
    }

    return () => clearInterval(timerRef.current);
  }, [isRecording]);

  // Format time for display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type === 'audio/wav') {
        setStatus("Processing dropped file...");
        await uploadAudio(file);
      } else {
        setError("Please drop a .wav file");
      }
    }
  };

  const startAudioVisualization = (stream) => {
    // Only create a new audio context if one doesn't exist
    if (!audioContextRef.current || audioContextRef.current.state === 'closed') {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    analyserRef.current = audioContextRef.current.createAnalyser();
    const source = audioContextRef.current.createMediaStreamSource(stream);
    source.connect(analyserRef.current);

    // Configure analyser
    analyserRef.current.fftSize = 256;
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const updateAudioLevel = () => {
      if (!isRecording) {
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
        return;
      }

      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((acc, val) => acc + val, 0) / bufferLength;
      const normalizedLevel = average / 256;
      setAudioLevel(normalizedLevel);

      animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    };

    updateAudioLevel();
  };

  const startRecording = async () => {
    try {
      setError(null);
      setStatus("Requesting microphone access...");
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          deviceId: selectedDevice ? { exact: selectedDevice } : undefined,
          channelCount: 1,
          sampleRate: 48000,
          echoCancellation: true,
          noiseSuppression: true,
        }
      });
      
      audioStreamRef.current = stream;
      startAudioVisualization(stream);
      
      const recorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 128000
      });
      
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm;codecs=opus' });
        setAudioPreview(URL.createObjectURL(blob));
        await uploadAudio(blob);
        chunksRef.current = [];
      };
      
      recorder.start(1000);
      setMediaRecorder(recorder);
      setIsRecording(true);
      setStatus("Recording...");
    } catch (err) {
      setError(`Could not start recording: ${err.message}`);
      setStatus("Failed to start recording");
      console.error("Error starting recording:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      setStatus("Stopping recording...");
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const uploadAudio = async (fileOrBlob) => {
    const formData = new FormData();
    
    if (fileOrBlob instanceof Blob) {
      console.log('Uploading blob of size:', fileOrBlob.size, 'bytes');  // Debug log
      const file = new File([fileOrBlob], "recording.webm", { 
        type: "audio/webm;codecs=opus" 
      });
      formData.append("file", file);
    } else {
      console.log('Uploading file of size:', fileOrBlob.size, 'bytes');  // Debug log
      formData.append("file", fileOrBlob);
    }

    try {
      setStatus("Uploading recording...");
      const response = await axios.post("http://localhost:8000/api/entries/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      console.log("Upload response:", response.data);  // Debug log
      setStatus(`Upload successful! Transcription: ${response.data.transcription}`);
    } catch (error) {
      console.error("Upload error:", error);  // Debug log
      setError(`Upload failed: ${error.message}`);
      setStatus("Upload failed");
    }
  };

  return (
    <div style={{ 
      padding: '20px',
      maxWidth: '600px',
      margin: '0 auto',
      textAlign: 'center'
    }}>
      {/* Device Selection */}
      <div style={{
        marginBottom: '2rem',
      }}>
        <label style={{
          display: 'block',
          marginBottom: '0.5rem',
          fontWeight: '500'
        }}>
          Select Microphone:
        </label>
        <select
          value={selectedDevice}
          onChange={(e) => setSelectedDevice(e.target.value)}
          disabled={isRecording}
          style={{
            width: '100%',
            padding: '0.5rem',
            borderRadius: '8px',
            border: '1px solid #e9ecef',
            backgroundColor: isRecording ? '#f8f9fa' : 'white'
          }}
        >
          {audioDevices.map(device => (
            <option key={device.deviceId} value={device.deviceId}>
              {device.label || `Microphone ${device.deviceId.slice(0, 5)}...`}
            </option>
          ))}
        </select>
      </div>

      {/* Recording Timer */}
      {isRecording && (
        <div style={{
          fontSize: '2rem',
          fontWeight: '600',
          color: '#00b894',
          marginBottom: '1rem'
        }}>
          {formatTime(recordingTime)}
        </div>
      )}

      {/* Audio Level Visualization */}
      <div style={{
        width: '100%',
        height: '40px',
        backgroundColor: '#f0f0f0',
        borderRadius: '20px',
        overflow: 'hidden',
        marginBottom: '20px',
        position: 'relative'
      }}>
        <div style={{
          width: `${audioLevel * 100}%`,
          height: '100%',
          backgroundColor: isRecording ? '#00b894' : '#ccc',
          transition: 'width 0.1s ease-out',
          borderRadius: '20px'
        }} />
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: '#2d3436',
          fontWeight: '500',
          mixBlendMode: 'difference'
        }}>
          {isRecording ? 'Recording Level' : 'Ready'}
        </div>
      </div>

      {/* Status and Error Messages */}
      <div style={{
        marginBottom: '20px',
        padding: '1rem',
        backgroundColor: error ? '#fff3f3' : '#f8f9fa',
        borderRadius: '8px',
        color: error ? '#ff7675' : '#2d3436',
        border: error ? '1px solid #ff7675' : '1px solid #e9ecef'
      }}>
        {error || status}
      </div>

      {/* Control Buttons */}
      <div style={{
        display: 'flex',
        gap: '1rem',
        justifyContent: 'center',
        marginBottom: '2rem'
      }}>
        <button 
          onClick={startRecording} 
          disabled={isRecording}
          style={{
            padding: '1rem 2rem',
            backgroundColor: isRecording ? '#ccc' : '#00b894',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isRecording ? 'not-allowed' : 'pointer',
            fontWeight: '500',
            transition: 'all 0.2s ease',
            fontSize: '1rem'
          }}
        >
          {isRecording ? 'Recording...' : 'Start Recording'}
        </button>
        <button 
          onClick={stopRecording} 
          disabled={!isRecording}
          style={{
            padding: '1rem 2rem',
            backgroundColor: !isRecording ? '#ccc' : '#ff7675',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: !isRecording ? 'not-allowed' : 'pointer',
            fontWeight: '500',
            transition: 'all 0.2s ease',
            fontSize: '1rem'
          }}
        >
          Stop Recording
        </button>
      </div>

      {/* Audio Preview */}
      {audioPreview && (
        <div style={{
          marginTop: '2rem',
          padding: '1rem',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef'
        }}>
          <h3 style={{ marginBottom: '1rem' }}>Preview Recording</h3>
          <audio 
            src={audioPreview} 
            controls 
            style={{ width: '100%' }}
          />
        </div>
      )}

      {/* Recording Tips */}
      <div style={{
        marginTop: '2rem',
        padding: '1rem',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        border: '1px solid #e9ecef',
        textAlign: 'left'
      }}>
        <h3 style={{ marginBottom: '1rem' }}>Recording Tips</h3>
        <ul style={{ paddingLeft: '1.5rem' }}>
          <li>Speak clearly and at a normal pace</li>
          <li>Keep the microphone about 6-12 inches from your mouth</li>
          <li>Avoid background noise when possible</li>
          <li>Watch the level meter to ensure good audio levels</li>
        </ul>
      </div>

      <style>
        {`
          @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
          }
        `}
      </style>
    </div>
  );
}

export default AudioRecorder;
