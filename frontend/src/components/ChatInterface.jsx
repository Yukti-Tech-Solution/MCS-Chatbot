/**
 * Chat Interface Component
 * Main chat component with message history and input handling
 */
import React, { useState, useEffect, useRef } from 'react';
import Message from './Message';
import InputBox from './InputBox';
import { sendMessage } from '../api';

function ChatInterface() {
  // State management
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Ref for auto-scrolling
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Scroll to bottom function
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Handle sending a message
  const handleSend = async () => {
    const question = inputText.trim();
    
    if (!question || loading) {
      return;
    }

    // Clear any previous errors
    setError(null);

    // Add user message to chat
    const userMessage = {
      role: 'user',
      content: question,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    try {
      // Call API to get response
      const response = await sendMessage(question);

      // Add assistant response to chat
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources || []
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      // Handle error
      console.error('Error sending message:', err);
      setError(err.message || 'Failed to get response. Please try again.');

      // Add error message to chat
      const errorMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${err.message || 'Failed to get response. Please check your connection and try again.'}`,
        timestamp: new Date(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // Handle input change
  const handleInputChange = (value) => {
    setInputText(value);
    setError(null); // Clear error when user starts typing
  };

  // Container styles
  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    overflow: 'hidden',
    background: '#343541'
  };

  // Messages container styles
  const messagesContainerStyle = {
    flex: 1,
    overflowY: 'auto',
    overflowX: 'hidden',
    padding: '24px 0 0',
    background: '#343541'
  };

  // Centered inner wrapper for messages and welcome
  const innerMessagesWrapper = {
    maxWidth: '900px',
    margin: '0 auto',
    width: '100%',
    padding: '0 32px'
  };

  // Welcome message (shown when no messages)
  const welcomeTitleStyle = {
    color: '#ececf1',
    fontSize: '28px',
    fontWeight: 700,
    textAlign: 'center',
    marginTop: '40px',
    marginBottom: '12px'
  };

  const welcomeSubtitleStyle = {
    color: '#8e8ea0',
    fontSize: '16px',
    textAlign: 'center',
    marginBottom: '24px',
    lineHeight: 1.7
  };

  const examplesGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: '12px',
    margin: '0 auto',
    maxWidth: '800px'
  };

  const exampleButtonStyle = {
    background: '#40414f',
    border: '1px solid #565869',
    color: '#ececf1',
    padding: '14px 16px',
    borderRadius: '12px',
    fontSize: '15px',
    textAlign: 'left',
    cursor: 'pointer',
    transition: 'background-color 0.15s, border-color 0.15s, box-shadow 0.15s',
    boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
  };

  const exampleButtonHover = {
    background: '#494b59',
    borderColor: '#6b6d7a'
  };

  // Error banner styles
  const errorBannerStyle = {
    padding: '12px 24px',
    background: '#8b2635',
    color: '#fff',
    fontSize: '14px',
    textAlign: 'center',
    borderBottom: '1px solid #4d4d4f'
  };

  return (
    <div style={containerStyle}>
      {/* Error Banner */}
      {error && (
        <div style={errorBannerStyle}>
          ⚠️ {error}
        </div>
      )}

      {/* Messages Container */}
      <div 
        ref={messagesContainerRef}
        style={messagesContainerStyle}
      >
        <div style={innerMessagesWrapper}>
          {/* Show welcome message if no messages */}
          {messages.length === 0 && (
            <div>
              <div style={welcomeTitleStyle}>MCS Act Legal Assistant</div>
              <div style={welcomeSubtitleStyle}>
                Ask anything about the Maharashtra Cooperative Societies Act. I’ll answer using the official documents and provide citations.
              </div>
              <div style={examplesGridStyle}>
                {[
                  'What are the requirements for forming a cooperative society?',
                  'What is the procedure for registration?',
                  'What are the rights and duties of members?',
                  'How is the management committee elected?'
                ].map((text, idx) => (
                  <button
                    key={idx}
                    style={exampleButtonStyle}
                    onMouseEnter={(e) => { e.currentTarget.style.background = exampleButtonHover.background; e.currentTarget.style.borderColor = exampleButtonHover.borderColor; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = '#40414f'; e.currentTarget.style.borderColor = '#565869'; }}
                    onClick={() => {
                      setInputText(text);
                      setTimeout(handleSend, 0);
                    }}
                  >
                    {text}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Render all messages */}
          {messages.map((message, index) => (
            <Message
              key={index}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
            />
          ))}

          {/* Loading indicator */}
          {loading && (
            <div style={{
              display: 'flex',
              justifyContent: 'flex-start',
              padding: '12px 24px'
            }}>
              <div style={{
                maxWidth: '90%', // wider bubble
                padding: '20px 24px', // increased padding
                borderRadius: '12px',
                background: '#444654',
                color: '#ececf1',
                fontSize: '17px', // larger font
                lineHeight: 1.7, // better line height
                boxShadow: '0 4px 16px rgba(0,0,0,0.2)'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <div style={{
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#8e8ea0',
                    marginBottom: '8px'
                  }}>
                    Assistant
                  </div>
                </div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: '#8e8ea0'
                }}>
                  <span className="loading-dots">
                    <span>.</span>
                    <span>.</span>
                    <span>.</span>
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Scroll anchor */}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Box */}
      <InputBox
        value={inputText}
        onChange={handleInputChange}
        onSend={handleSend}
        disabled={loading}
        loading={loading}
      />

      {/* Loading dots animation */}
      <style>{`
        .loading-dots {
          display: inline-flex;
          gap: 4px;
        }
        .loading-dots span {
          animation: loading-dot 1.4s infinite;
          animation-delay: calc(var(--i) * 0.2s);
        }
        .loading-dots span:nth-child(1) {
          --i: 0;
        }
        .loading-dots span:nth-child(2) {
          --i: 1;
        }
        .loading-dots span:nth-child(3) {
          --i: 2;
        }
        @keyframes loading-dot {
          0%, 60%, 100% {
            opacity: 0.3;
            transform: translateY(0);
          }
          30% {
            opacity: 1;
            transform: translateY(-4px);
          }
        }
      `}</style>
    </div>
  );
}

export default ChatInterface;

