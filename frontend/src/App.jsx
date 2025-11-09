/**
 * Main App Component
 * Renders the chat application with header and chat interface
 */
import React from 'react';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div style={{ 
      height: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      background: '#343541'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px',
        borderBottom: '1px solid #4d4d4f',
        textAlign: 'center',
        background: '#202123',
        flexShrink: 0
      }}>
        <h1 style={{ 
          fontSize: '20px', 
          fontWeight: 600,
          color: '#fff',
          margin: 0
        }}>
          MCS Act Legal Assistant
        </h1>
        <p style={{
          fontSize: '12px',
          color: '#8e8ea0',
          margin: '4px 0 0 0'
        }}>
          Ask questions about Maharashtra Cooperative Societies Act
        </p>
      </div>

      {/* Chat Interface */}
      <ChatInterface />
    </div>
  );
}

export default App;

