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
      console.error("Error parsing JSON:", e);
      return [];
    }
  };

  // Helper function to generate a string representation of an event object.
  const getEventString = (event) => {
    if (typeof event === "object" && event !== null) {
      const parts = [];
      if (event.subject) parts.push(event.subject);
      if (event.action) parts.push(event.action);
      if (event.object) parts.push(event.object);
      if (event.time && event.time.length > 0) {
        parts.push(`(Time: ${event.time.join(", ")})`);
      }
      if (event.location && event.location.length > 0) {
        parts.push(`(Location: ${event.location.join(", ")})`);
      }
      if (event.additional_info && event.additional_info.length > 0) {
        parts.push(`(Info: ${event.additional_info.join(", ")})`);
      }
      return parts.join(" ");
    }
    return event;
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2
        style={{
          fontSize: "1.8rem",
          fontWeight: "600",
          marginBottom: "1.5rem",
          color: "#2d3436",
        }}
      >
        Timeline
      </h2>

      {entries.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "2rem",
            color: "#666",
          }}
        >
          No entries yet. Start by recording your first voice entry!
        </div>
      ) : (
        entries.map((entry) => (
          <div
            key={entry.id}
            style={{
              padding: "1.5rem",
              backgroundColor: "#ffffff",
              borderRadius: "12px",
              border: "1px solid #e9ecef",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              marginBottom: "1.5rem",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "1rem",
              }}
            >
              <span
                style={{
                  color: "#00b894",
                  fontWeight: "500",
                }}
              >
                {entry.created_at
                  ? new Date(entry.created_at?.seconds * 1000).toLocaleString()
                  : "No date"}
              </span>
              <span
                style={{
                  backgroundColor: getSentimentColor(entry.sentiment_score || 0),
                  color: "white",
                  padding: "0.25rem 0.75rem",
                  borderRadius: "999px",
                  fontSize: "0.875rem",
                }}
              >
                Sentiment: {(entry.sentiment_score || 0).toFixed(2)}
              </span>
            </div>

            {/* Transcription */}
            <p
              style={{
                margin: "0 0 1rem 0",
                fontSize: "1rem",
                lineHeight: "1.5",
                color: "#333",
              }}
            >
              {entry.transcription || "No transcription available"}
            </p>

            {/* Related Events */}
            <div style={{ fontSize: "0.8rem", color: "#555" }}>
              {safeParseJSON(entry.events_tagged).length > 0 && (
                <div style={{ marginBottom: "0.5rem", fontStyle: "italic" }}>
                  Related Event
                  {safeParseJSON(entry.events_tagged).length > 1 ? "s" : ""}:
                </div>
              )}
              {safeParseJSON(entry.events_tagged).map((eventItem, index) => (
                <div key={index} style={{ marginBottom: "0.25rem" }}>
                  {getEventString(eventItem)}
                </div>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function getSentimentColor(score) {
  if (score > 0.5) return "#00b894"; // Positive
  if (score < -0.5) return "#ff7675"; // Negative
  return "#fdcb6e"; // Neutral
}

export default Timeline;
