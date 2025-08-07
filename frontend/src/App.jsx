import { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import SearchResults from './components/SearchResults';
import AddLinkModal from './components/AddLinkModal';
import LinksSidebar from './components/LinksSidebar';
import linksAPI from './api/links';
import './App.css';

function App() {
  const [links, setLinks] = useState([]);
  const [searchResults, setSearchResults] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [loadingLinks, setLoadingLinks] = useState(true);
  const [message, setMessage] = useState(null);
  const [searchError, setSearchError] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Fetch links on component mount
  useEffect(() => {
    fetchLinks();
  }, []);

  const fetchLinks = async () => {
    try {
      setLoadingLinks(true);
      const data = await linksAPI.getLinks();
      setLinks(data);
    } catch (error) {
      console.error('Error fetching links:', error);
      showMessage('Failed to fetch links', 'error');
    } finally {
      setLoadingLinks(false);
    }
  };

  const handleSearch = async (query) => {
    if (!query.trim()) return;
    
    setSearchQuery(query);
    setSearchLoading(true);
    setSearchError(null);
    setSearchResults(null);
    
    try {
      const results = await linksAPI.searchLinks(query);
      setSearchResults(results);
      if (results.length === 0) {
        showMessage('No results found. Try adding more links to your knowledge base.', 'info');
      }
    } catch (error) {
      console.error('Error searching:', error);
      setSearchError(error.message || 'Failed to search. Please try again.');
      showMessage('Search failed. Please try again.', 'error');
    } finally {
      setSearchLoading(false);
    }
  };

  const handleAddLink = async (linkData) => {
    try {
      setLoading(true);
      const newLink = await linksAPI.createLink(linkData);
      setLinks(prevLinks => [newLink, ...prevLinks]);
      showMessage('Link saved successfully!', 'success');
      setIsAddModalOpen(false);
    } catch (error) {
      console.error('Error saving link:', error);
      showMessage('Failed to save link. Please try again.', 'error');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteLink = async (linkId) => {
    try {
      await linksAPI.deleteLink(linkId);
      setLinks(prevLinks => prevLinks.filter(link => link._id !== linkId));
      showMessage('Link deleted successfully', 'success');
    } catch (error) {
      console.error('Error deleting link:', error);
      showMessage('Failed to delete link', 'error');
    }
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 5000);
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-container">
          <div className="header-left">
            <h1 className="app-title">🔗 KnowledgeLink</h1>
            <p className="app-subtitle">Your AI-Powered Knowledge Base</p>
          </div>
          <button 
            className="menu-button"
            onClick={toggleSidebar}
            aria-label="Toggle links sidebar"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="3" y1="12" x2="21" y2="12" strokeWidth="2" strokeLinecap="round"/>
              <line x1="3" y1="6" x2="21" y2="6" strokeWidth="2" strokeLinecap="round"/>
              <line x1="3" y1="18" x2="21" y2="18" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            {links.length > 0 && (
              <span className="link-count-badge">{links.length}</span>
            )}
          </button>
        </div>
      </header>

      <main className="app-main">
        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <div className="search-section">
          <SearchBar 
            onSearch={handleSearch}
            onAddClick={() => setIsAddModalOpen(true)}
          />
        </div>

        {(searchResults || searchLoading || searchError) && (
          <SearchResults 
            results={searchResults}
            loading={searchLoading}
            error={searchError}
            query={searchQuery}
          />
        )}

        {!searchResults && !searchLoading && !searchError && (
          <div className="welcome-section">
            <div className="welcome-card">
              <h2>Welcome to KnowledgeLink</h2>
              <p>Your personal knowledge management system with AI-powered search</p>
              
              <div className="features-grid">
                <div className="feature-card">
                  <div className="feature-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="11" cy="11" r="8" strokeWidth="2"/>
                      <path d="m21 21-4.35-4.35" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                  </div>
                  <h3>Smart Search</h3>
                  <p>Search through your saved content using AI-powered semantic search</p>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" strokeWidth="2" strokeLinecap="round"/>
                      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                  </div>
                  <h3>Save Links</h3>
                  <p>Add links to build your knowledge base with automatic content extraction</p>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M12 2L2 7l10 5 10-5-10-5z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M2 17l10 5 10-5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M2 12l10 5 10-5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <h3>Organize</h3>
                  <p>Tag and categorize your links for better organization</p>
                </div>
              </div>

              <div className="quick-actions">
                <button 
                  className="primary-action-btn"
                  onClick={() => setIsAddModalOpen(true)}
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <line x1="12" y1="5" x2="12" y2="19" strokeWidth="2" strokeLinecap="round"/>
                    <line x1="5" y1="12" x2="19" y2="12" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  Add Your First Link
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      <AddLinkModal 
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={handleAddLink}
        loading={loading}
      />

      <LinksSidebar 
        links={links}
        onDelete={handleDeleteLink}
        loading={loadingLinks}
        isOpen={isSidebarOpen}
        onToggle={toggleSidebar}
      />
    </div>
  );
}

export default App;