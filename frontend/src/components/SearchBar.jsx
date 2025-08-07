import { useState } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch, onAddClick }) => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || isSearching) return;
    
    setIsSearching(true);
    try {
      await onSearch(query);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="search-bar-container">
      <form className="search-form" onSubmit={handleSubmit}>
        <div className="search-input-wrapper">
          <input
            type="text"
            className="search-input"
            placeholder="Search your knowledge base..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isSearching}
          />
          <button
            type="submit"
            className="search-button"
            disabled={!query.trim() || isSearching}
            aria-label="Search"
          >
            {isSearching ? (
              <svg className="search-icon spinning" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10" strokeWidth="2" strokeDasharray="30 70"/>
              </svg>
            ) : (
              <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="11" cy="11" r="8" strokeWidth="2"/>
                <path d="m21 21-4.35-4.35" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            )}
          </button>
        </div>
        <button
          type="button"
          className="add-link-button"
          onClick={onAddClick}
          aria-label="Add new link"
          title="Add new link"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="12" y1="5" x2="12" y2="19" strokeWidth="2" strokeLinecap="round"/>
            <line x1="5" y1="12" x2="19" y2="12" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
      </form>
    </div>
  );
};

export default SearchBar;
