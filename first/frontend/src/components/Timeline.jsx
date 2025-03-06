// frontend/src/components/Timeline.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

function Timeline() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    axios
      .get("http://localhost:8000/api/timeline")
      .then((res) => setEntries(res.data))
      .catch((err) => console.error(err));
  }, []);

  // Helper function to safely parse JSON
  const safeParseJSON = (jsonString) => {
    try {
      const parsed = JSON.parse(jsonString);
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      console.error('Error parsing JSON:', e);
      return [];
    }
  };

  return (
    <div>
      <h2 style={{
        fontSize: '1.5rem',
        fontWeight: '600',
        marginBottom: '1.5rem',
        color: '#2d3436'
      }}>Timeline</h2>
      
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem'
      }}>
        {entries.map((entry) => (
          <div key={entry.id} style={{
            padding: '1.5rem',
            backgroundColor: '#f8f9fa',
            borderRadius: '12px',
            border: '1px solid #e9ecef'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1rem'
            }}>
              <span style={{
                color: '#00b894',
                fontWeight: '500'
              }}>
                {entry.created_at ? new Date(entry.created_at?.seconds * 1000).toLocaleString() : 'No date'}
              </span>
              <span style={{
                backgroundColor: getSentimentColor(entry.sentiment_score || 0),
                color: 'white',
                padding: '0.25rem 0.75rem',
                borderRadius: '999px',
                fontSize: '0.875rem'
              }}>
                Sentiment: {(entry.sentiment_score || 0).toFixed(2)}
              </span>
            </div>
            
            <p style={{
              margin: '0 0 1rem 0',
              fontSize: '1rem',
              lineHeight: '1.5'
            }}>{entry.transcription || 'No transcription available'}</p>
            
            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '0.5rem'
            }}>
              {safeParseJSON(entry.events_tagged).map((event, index) => (
                <span key={index} style={{
                  backgroundColor: '#e9ecef',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '999px',
                  fontSize: '0.875rem'
                }}>
                  {event}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {entries.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '2rem',
          color: '#666'
        }}>
          No entries yet. Start by recording your first voice entry!
        </div>
      )}
    </div>
  );
}

function getSentimentColor(score) {
  if (score > 0.5) return '#00b894';  // Positive
  if (score < -0.5) return '#ff7675'; // Negative
  return '#fdcb6e';                   // Neutral
}

export default Timeline;
