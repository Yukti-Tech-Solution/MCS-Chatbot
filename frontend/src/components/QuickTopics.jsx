/**
 * QuickTopics Component
 * Displays quick topic buttons for common MCS Act queries
 * Helps users quickly start conversations with pre-defined questions
 */
import React from 'react';

function QuickTopics({ onTopicClick, disabled }) {
  // Common topics with icons and queries
  const topics = [
    { 
      icon: '🏢', 
      text: 'How to register a society?', 
      query: 'What is the procedure for registering a new cooperative society?' 
    },
    { 
      icon: '👥', 
      text: 'Member rights & duties', 
      query: 'What are the rights and duties of society members?' 
    },
    { 
      icon: '💰', 
      text: 'Maintenance charges', 
      query: 'What are the rules for collecting maintenance charges in a society?' 
    },
    { 
      icon: '⚖️', 
      text: 'Dispute resolution', 
      query: 'How to resolve disputes between society members?' 
    },
    { 
      icon: '📊', 
      text: 'Annual meetings', 
      query: 'What are the requirements for conducting Annual General Meetings?' 
    },
    { 
      icon: '🏗️', 
      text: 'Repairs & renovation', 
      query: 'What are the rules for major repairs and renovations in society?' 
    },
  ];

  return (
    <div style={{
      padding: '20px 24px',
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '12px',
      maxWidth: '900px',
      margin: '0 auto'
    }}>
      {/* Section header */}
      <h3 style={{
        gridColumn: '1 / -1',
        fontSize: '14px',
        fontWeight: 600,
        color: '#8e8ea0',
        marginBottom: '8px',
        textTransform: 'uppercase',
        letterSpacing: '0.5px'
      }}>
        Quick Topics:
      </h3>

      {/* Topic buttons */}
      {topics.map((topic, index) => (
        <button
          key={index}
          onClick={() => !disabled && onTopicClick(topic.query)}
          disabled={disabled}
          style={{
            padding: '12px 16px',
            background: '#2d2e38',
            border: '1px solid #4d4d4f',
            borderRadius: '10px',
            color: '#ececf1',
            fontSize: '13px',
            cursor: disabled ? 'not-allowed' : 'pointer',
            textAlign: 'left',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s',
            opacity: disabled ? 0.5 : 1
          }}
          onMouseEnter={(e) => {
            if (!disabled) {
              e.target.style.background = '#3d3e48';
              e.target.style.borderColor = '#5d5e68';
            }
          }}
          onMouseLeave={(e) => {
            if (!disabled) {
              e.target.style.background = '#2d2e38';
              e.target.style.borderColor = '#4d4d4f';
            }
          }}
        >
          {/* Icon */}
          <span style={{ fontSize: '18px' }}>{topic.icon}</span>
          
          {/* Topic text */}
          <span>{topic.text}</span>
        </button>
      ))}
    </div>
  );
}

export default QuickTopics;

