import './SearchResults.css';

const SearchResults = ({ results, loading, error, query }) => {
  if (loading) {
    return (
      <div className="search-results">
        <div className="search-loading">
          <div className="loading-spinner"></div>
          <p>Searching for "{query}"...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="search-results">
        <div className="search-error">
          <svg className="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" strokeWidth="2"/>
            <line x1="12" y1="8" x2="12" y2="12" strokeWidth="2" strokeLinecap="round"/>
            <line x1="12" y1="16" x2="12.01" y2="16" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <h3>Search Failed</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!results || results.length === 0) {
    if (query) {
      return (
        <div className="search-results">
          <div className="no-results">
            <svg className="no-results-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8" strokeWidth="2"/>
              <path d="m21 21-4.35-4.35" strokeWidth="2" strokeLinecap="round"/>
              <line x1="8" y1="11" x2="14" y2="11" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <h3>No results found</h3>
            <p>Try searching with different keywords</p>
          </div>
        </div>
      );
    }
    return null;
  }

  const highlightText = (text, query) => {
    if (!query || !text) return text;
    
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, i) => 
      part.toLowerCase() === query.toLowerCase() ? 
        <mark key={i}>{part}</mark> : part
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="search-results">
      <div className="results-header">
        <h2>Search Results</h2>
        <span className="results-count">{results.length} {results.length === 1 ? 'result' : 'results'} found</span>
      </div>
      
      <div className="results-list">
        {results.map((result) => (
          <div key={result.link_id} className="result-card">
            <div className="result-header">
              <a 
                href={result.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="result-title"
              >
                {highlightText(result.title || 'Untitled', query)}
              </a>
              <span className="result-score" title="Relevance score">
                {Math.round(result.score * 100)}%
              </span>
            </div>
            
            <div className="result-url">
              {result.url}
            </div>
            
            {result.matching_chunks && result.matching_chunks.length > 0 && (
              <div className="result-chunks">
                {result.matching_chunks.slice(0, 2).map((chunk, index) => (
                  <div key={index} className="chunk-preview">
                    <p>{highlightText(chunk.text, query)}</p>
                    <span className="chunk-score">Match: {Math.round(chunk.score * 100)}%</span>
                  </div>
                ))}
                {result.matching_chunks.length > 2 && (
                  <div className="more-chunks">
                    +{result.matching_chunks.length - 2} more matching sections
                  </div>
                )}
              </div>
            )}
            
            {result.tags && result.tags.length > 0 && (
              <div className="result-tags">
                {result.tags.map((tag, index) => (
                  <span key={index} className="result-tag">
                    {tag}
                  </span>
                ))}
              </div>
            )}
            
            <div className="result-meta">
              <span className="result-date">Added {formatDate(result.created_at)}</span>
              <span className="result-domain">
                {new URL(result.url).hostname.replace('www.', '')}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchResults;
