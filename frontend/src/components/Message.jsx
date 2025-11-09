/**
 * Message Component
 * Displays individual chat messages with role-based styling
 */
import React from 'react';

/**
 * Message component for displaying chat messages
 * 
 * @param {Object} props
 * @param {string} props.role - 'user' or 'assistant'
 * @param {string} props.content - Message content
 * @param {Date} props.timestamp - Optional timestamp
 */
function Message({ role, content, timestamp }) {
  // Determine styling based on role
  const isUser = role === 'user';
  
  // Container styles
  const containerStyle = {
    display: 'flex',
    justifyContent: isUser ? 'flex-end' : 'flex-start',
    padding: '12px 24px',
    width: '100%'
  };

  // Message bubble styles
  const messageStyle = {
    maxWidth: '85%',
    padding: '16px 20px',
    borderRadius: '8px',
    background: isUser ? '#343541' : '#444654',
    color: '#ececf1',
    fontSize: '16px',
    lineHeight: '1.6',
    wordWrap: 'break-word',
    whiteSpace: 'pre-wrap', // Preserve line breaks
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
  };

  // Role label styles
  const labelStyle = {
    fontSize: '12px',
    fontWeight: 600,
    color: isUser ? '#10a37f' : '#8e8ea0',
    marginBottom: '8px',
    textTransform: 'capitalize'
  };

  // Timestamp styles
  const timestampStyle = {
    fontSize: '11px',
    color: '#8e8ea0',
    marginTop: '8px',
    textAlign: isUser ? 'right' : 'left'
  };

  // Format timestamp if provided
  const formatTime = (date) => {
    if (!date) return '';
    return new Date(date).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div style={containerStyle}>
      <div style={{ display: 'flex', flexDirection: 'column', width: '100%', alignItems: isUser ? 'flex-end' : 'flex-start' }}>
        <div style={messageStyle}>
          {/* Role label */}
          <div style={labelStyle}>
            {isUser ? 'You' : 'Assistant'}
          </div>
          
          {/* Message content */}
          <div style={{ color: '#ececf1' }}>
            {content}
          </div>
          
          {/* Timestamp */}
          {timestamp && (
            <div style={timestampStyle}>
              {formatTime(timestamp)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Message;

