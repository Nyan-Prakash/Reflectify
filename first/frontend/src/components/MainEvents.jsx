// frontend/src/components/MainEvents.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";

function MainEvents() {
  const [data, setData] = useState({ main_events: [], all_events: {} });

  useEffect(() => {
    axios
      .get("http://localhost:8000/api/events/main")
      .then((res) => setData(res.data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div>
      <h2 style={{
        fontSize: '1.5rem',
        fontWeight: '600',
        marginBottom: '1.5rem',
        color: '#2d3436'
      }}>Main Events</h2>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        {data.main_events.map((event) => (
          <div key={event} style={{
            padding: '1rem',
            backgroundColor: '#f8f9fa',
            borderRadius: '8px',
            border: '1px solid #e9ecef'
          }}>
            <p style={{ margin: 0, fontWeight: '500' }}>{event}</p>
          </div>
        ))}
      </div>

      <h3 style={{
        fontSize: '1.25rem',
        fontWeight: '600',
        marginBottom: '1rem',
        color: '#2d3436'
      }}>Event Frequency</h3>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
        gap: '1rem'
      }}>
        {Object.entries(data.all_events).map(([event, count]) => (
          <div key={event} style={{
            padding: '1rem',
            backgroundColor: '#f8f9fa',
            borderRadius: '8px',
            border: '1px solid #e9ecef',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{ fontWeight: '500' }}>{event}</span>
            <span style={{
              backgroundColor: '#00b894',
              color: 'white',
              padding: '0.25rem 0.75rem',
              borderRadius: '999px',
              fontSize: '0.875rem'
            }}>{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MainEvents;
