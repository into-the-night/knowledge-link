import { useState } from 'react';
import './LinkList.css';

const LinkList = ({ links, onDelete, loading }) => {
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (linkId) => {
    if (window.confirm('Are you sure you want to delete this link?')) {
      setDeletingId(linkId);
      try {
        await onDelete(linkId);
      } finally {
        setDeletingId(null);
      }
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateText = (text, maxLength = 150) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <div className="links-container">
        <div className="loading">Loading links...</div>
      </div>
    );
  }

  if (!links || links.length === 0) {
    return (
      <div className="links-container">
        <div className="no-links">
          <h3>No links saved yet</h3>
          <p>Start by adding your first link using the form above!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="links-container">
      <h2>Saved Links ({links.length})</h2>
      <div className="links-grid">
        {links.map((link) => (
          <div key={link._id} className="link-card">
            <div className="link-header">
              <h3 className="link-title">
                <a href={link.url} target="_blank" rel="noopener noreferrer">
                  {link.title || 'Untitled'}
                </a>
              </h3>
              <button
                className="delete-btn"
                onClick={() => handleDelete(link._id)}
                disabled={deletingId === link._id}
                title="Delete link"
              >
                {deletingId === link._id ? '...' : '×'}
              </button>
            </div>
            
            <p className="link-url">{link.url}</p>
            
            {link.description && (
              <p className="link-description">
                {truncateText(link.description)}
              </p>
            )}
            
            {link.tags && link.tags.length > 0 && (
              <div className="link-tags">
                {link.tags.map((tag, index) => (
                  <span key={index} className="tag">
                    {tag}
                  </span>
                ))}
              </div>
            )}
            
            <div className="link-footer">
              <span className="link-date">
                Added: {formatDate(link.created_at)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LinkList;
