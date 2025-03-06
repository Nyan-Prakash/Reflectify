// frontend/src/App.jsx
import React, { useState } from "react";
import AudioRecorder from "./components/AudioRecorder";
import Timeline from "./components/Timeline";
import MainEvents from "./components/MainEvents";

function App() {
  const [activeTab, setActiveTab] = useState('record');

  return (
    <div style={{ 
      minHeight: '100vh',
      backgroundColor: '#f8f9fa',
      color: '#2d3436'
    }}>
      {/* Navigation Bar */}
      <nav style={{
        backgroundColor: 'white',
        padding: '1rem',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '2rem'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h1 style={{ 
            margin: 0,
            fontSize: '1.5rem',
            fontWeight: '600',
            color: '#00b894'
          }}>
            Reflectify
          </h1>
          <div style={{
            display: 'flex',
            gap: '1rem'
          }}>
            {['record', 'timeline', 'events'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  padding: '0.5rem 1rem',
                  border: 'none',
                  borderRadius: '8px',
                  backgroundColor: activeTab === tab ? '#00b894' : 'transparent',
                  color: activeTab === tab ? 'white' : '#2d3436',
                  cursor: 'pointer',
                  fontWeight: '500',
                  transition: 'all 0.2s ease',
                }}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 1rem'
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '2rem',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          {activeTab === 'record' && <AudioRecorder />}
          {activeTab === 'timeline' && <Timeline />}
          {activeTab === 'events' && <MainEvents />}
        </div>
      </main>
    </div>
  );
}

export default App;
