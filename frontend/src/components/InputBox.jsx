/**
 * Input Box Component
 * Handles user input with textarea and send button
 */
import React, { useState, useRef, useEffect } from 'react';

/**
 * InputBox component for chat input
 * 
 * @param {Object} props
 * @param {string} props.value - Current input value
 * @param {Function} props.onChange - Callback when input changes
 * @param {Function} props.onSend - Callback when send is triggered
 * @param {boolean} props.disabled - Whether input is disabled
 * @param {boolean} props.loading - Whether a request is in progress
 */
function InputBox({ value, onChange, onSend, disabled, loading }) {
  const textareaRef = useRef(null);
  const [textareaHeight, setTextareaHeight] = useState('auto');

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      // Reset height to auto to get correct scrollHeight
      textareaRef.current.style.height = 'auto';
      // Set height based on content, max 200px
      const newHeight = Math.min(textareaRef.current.scrollHeight, 200);
      setTextareaHeight(`${newHeight}px`);
      textareaRef.current.style.height = `${newHeight}px`;
    }
  }, [value]);

  // Handle input change
  const handleChange = (e) => {
    onChange(e.target.value);
  };

  // Handle key press
  const handleKeyDown = (e) => {
    // Enter key sends message (unless Shift is held)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && !loading && value.trim()) {
        onSend();
      }
    }
  };

  // Handle send button click
  const handleSend = () => {
    if (!disabled && !loading && value.trim()) {
      onSend();
    }
  };

  // Outer container to center the input area and add bottom padding
  const outerContainerStyle = {
    padding: '24px 32px', // More bottom padding and horizontal padding
    background: '#343541',
    borderTop: '1px solid #4d4d4f'
  };

  // Inner container with glow and max-width centering
  const innerContainerStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    maxWidth: '800px',
    margin: '0 auto',
    width: '100%',
    boxShadow: '0 -1px 12px rgba(25, 195, 125, 0.06)', // subtle top border glow
  };

  // Textarea styles
  const textareaStyle = {
    flex: 1,
    minHeight: '52px', // increase min height
    maxHeight: '200px',
    height: textareaHeight,
    padding: '16px 20px', // more padding
    background: '#40414f', // improved contrast
    border: '2px solid #565869', // more visible border
    borderRadius: '16px', // larger radius
    color: '#ececf1',
    fontSize: '17px', // larger font
    fontFamily: 'inherit',
    resize: 'none',
    outline: 'none',
    overflowY: 'auto',
    lineHeight: '1.5',
    transition: 'border-color 0.2s, box-shadow 0.2s',
    cursor: disabled ? 'not-allowed' : 'text',
    opacity: disabled ? 0.6 : 1,
    boxShadow: '0 0 15px rgba(0,0,0,0.3)' // subtle shadow
  };

  // Send button styles
  const sendButtonStyle = {
    width: '52px',
    height: '52px',
    minWidth: '52px',
    borderRadius: '50%', // circular
    background: value.trim() && !disabled && !loading ? '#19c37d' : '#565869', // ChatGPT green
    border: '2px solid transparent',
    color: '#fff',
    fontSize: '20px', // larger icon size
    cursor: value.trim() && !disabled && !loading ? 'pointer' : 'not-allowed',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'background-color 0.2s, transform 0.05s ease',
    opacity: value.trim() && !disabled && !loading ? 1 : 0.6,
    boxShadow: value.trim() && !disabled && !loading ? '0 6px 16px rgba(25,195,125,0.25)' : 'none'
  };

  // Hover effect for send button
  const handleMouseEnter = (e) => {
    if (value.trim() && !disabled && !loading) {
      e.target.style.background = '#17b073'; // darker shade on hover
    }
  };

  const handleMouseLeave = (e) => {
    if (value.trim() && !disabled && !loading) {
      e.target.style.background = '#19c37d';
    }
  };

  return (
    <div style={outerContainerStyle}>
      <div style={innerContainerStyle}>
        {/* Textarea */}
        <textarea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        disabled={disabled || loading}
        placeholder={disabled || loading ? "Please wait..." : "Ask about MCS Act... (Press Enter to send, Shift+Enter for new line)"}
        style={textareaStyle}
        rows={1}
        />

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={!value.trim() || disabled || loading}
          style={sendButtonStyle}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          title="Send message (Enter)"
        >
          {loading ? (
            // Loading spinner
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ animation: 'spin 1s linear infinite' }}
            >
              <path d="M21 12a9 9 0 11-6.219-8.56" />
            </svg>
          ) : (
            // Send icon (arrow)
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          )}
        </button>
      </div>

      {/* CSS for spinner animation */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default InputBox;

