/**
 * RelatedLinks Component
 * Displays relevant government resources and official links for MCS Act
 * Also includes PDF download button
 */
import React from 'react';

function RelatedLinks({ links, onDownloadPDF, question }) {
  // Don't render if no links provided
  if (!links || links.length === 0) return null;

  return (
    <div style={{
      margin: '20px 24px',
      padding: '20px',
      background: '#2d2e38',
      borderRadius: '12px',
      border: '1px solid #4d4d4f'
    }}>
      {/* Header */}
      <h3 style={{
        fontSize: '16px',
        fontWeight: 600,
        color: '#10a37f',
        marginBottom: '16px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <span>📚</span>
        <span>Related Resources</span>
      </h3>

      {/* Render each resource category */}
      {links.map((resource, idx) => (
        <div key={idx} style={{ marginBottom: '16px' }}>
          {/* Resource category title */}
          <h4 style={{
            fontSize: '14px',
            fontWeight: 600,
            color: '#ececf1',
            marginBottom: '8px'
          }}>
            {resource.title}
          </h4>

          {/* Render links in this category */}
          {resource.links && resource.links.map((link, linkIdx) => (
            <div key={linkIdx} style={{
              padding: '8px 12px',
              background: '#343541',
              borderRadius: '8px',
              marginBottom: '8px',
              transition: 'background 0.2s'
            }}>
              {/* Link */}
              <a
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: '#10a37f',
                  textDecoration: 'none',
                  fontSize: '13px',
                  fontWeight: 500,
                  display: 'block',
                  marginBottom: '4px'
                }}
                onMouseEnter={(e) => {
                  e.target.style.textDecoration = 'underline';
                }}
                onMouseLeave={(e) => {
                  e.target.style.textDecoration = 'none';
                }}
              >
                🔗 {link.name}
              </a>
              
              {/* Link description */}
              <p style={{
                fontSize: '12px',
                color: '#8e8ea0',
                margin: '4px 0 0 0',
                lineHeight: 1.5
              }}>
                {link.description}
              </p>
            </div>
          ))}
        </div>
      ))}

      {/* PDF Download Button */}
      {onDownloadPDF && question && (
        <button
          onClick={() => onDownloadPDF(question)}
          style={{
            width: '100%',
            padding: '12px',
            background: '#10a37f',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 600,
            cursor: 'pointer',
            marginTop: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => {
            e.target.style.background = '#0d8b6f';
          }}
          onMouseLeave={(e) => {
            e.target.style.background = '#10a37f';
          }}
        >
          <span>📄</span>
          <span>Download This Information as PDF</span>
        </button>
      )}
    </div>
  );
}

export default RelatedLinks;

