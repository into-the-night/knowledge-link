import { useState } from 'react';
import './LinksSidebar.css';

const LinksSidebar = ({ links, onDelete, loading, isOpen, onToggle }) => {
  const [deletingId, setDeletingId] = useState(null);
  const [searchFilter, setSearchFilter] = useState('');

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
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
      if (diffHours === 0) {
        const diffMinutes = Math.floor(diffTime / (1000 * 60));
        return `${diffMinutes} min ago`;
      }
      return `${diffHours} hours ago`;
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
      });
    }
  };

  const truncateText = (text, maxLength = 100) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const filteredLinks = links.filter(link => {
    if (!searchFilter) return true;
    const search = searchFilter.toLowerCase();
    return (
      link.title?.toLowerCase().includes(search) ||
      link.description?.toLowerCase().includes(search) ||
      link.url?.toLowerCase().includes(search) ||
      link.tags?.some(tag => tag.toLowerCase().includes(search))
    );
  });

  return (
    <>
      <div className={`sidebar-overlay ${isOpen ? 'active' : ''}`} onClick={onToggle} />
      <div className={`links-sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>Your Links</h2>
          <button className="sidebar-close" onClick={onToggle} aria-label="Close sidebar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18" strokeWidth="2" strokeLinecap="round"/>
              <line x1="6" y1="6" x2="18" y2="18" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        <div className="sidebar-search">
          <input
            type="text"
            placeholder="Filter links..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="sidebar-search-input"
          />
        </div>

        <div className="sidebar-content">
          {loading ? (
            <div className="sidebar-loading">Loading links...</div>
          ) : filteredLinks.length === 0 ? (
            <div className="sidebar-empty">
              {searchFilter ? (
                <>
                  <p>No links match your filter</p>
                  <button 
                    className="clear-filter-btn"
                    onClick={() => setSearchFilter('')}
                  >
                    Clear filter
                  </button>
                </>
              ) : (
                <>
                  <svg className="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" strokeWidth="2"/>
                    <polyline points="13 2 13 9 20 9" strokeWidth="2"/>
                  </svg>
                  <p>No links saved yet</p>
                  <p className="empty-hint">Click the + button to add your first link</p>
                </>
              )}
            </div>
          ) : (
            <div className="links-list">
              {filteredLinks.map((link) => (
                <div key={link._id} className="sidebar-link-item">
                  <div className="link-item-header">
                    <a 
                      href={link.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="link-item-title"
                      title={link.title || link.url}
                    >
                      {link.title || truncateText(link.url, 40)}
                    </a>
                    <button
                      className="link-delete-btn"
                      onClick={() => handleDelete(link._id)}
                      disabled={deletingId === link._id}
                      title="Delete link"
                    >
                      {deletingId === link._id ? (
                        <svg className="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <circle cx="12" cy="12" r="10" strokeWidth="2" strokeDasharray="30 70"/>
                        </svg>
                      ) : (
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <polyline points="3 6 5 6 21 6" strokeWidth="2"/>
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" strokeWidth="2"/>
                        </svg>
                      )}
                    </button>
                  </div>
                  
                  {link.description && (
                    <p className="link-item-description">
                      {truncateText(link.description, 80)}
                    </p>
                  )}
                  
                  {link.tags && link.tags.length > 0 && (
                    <div className="link-item-tags">
                      {link.tags.slice(0, 3).map((tag, index) => (
                        <span key={index} className="link-tag">
                          {tag}
                        </span>
                      ))}
                      {link.tags.length > 3 && (
                        <span className="link-tag more">+{link.tags.length - 3}</span>
                      )}
                    </div>
                  )}
                  
                  <div className="link-item-meta">
                    <span className="link-date">{formatDate(link.created_at)}</span>
                    <span className="link-domain">
                      {new URL(link.url).hostname.replace('www.', '')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="sidebar-footer">
          <div className="sidebar-stats">
            {links.length} {links.length === 1 ? 'link' : 'links'} saved
          </div>
        </div>
      </div>
    </>
  );
};

export default LinksSidebar;
