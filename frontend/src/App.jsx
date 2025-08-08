import { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import SearchResults from './components/SearchResults';
import AddLinkModal from './components/AddLinkModal';
import LinksSidebar from './components/LinksSidebar';
import { linksAPI, authAPI } from './api/links';
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
  const [currentUser, setCurrentUser] = useState(null);

  // Fetch links and check auth on component mount
  useEffect(() => {
    // Check for OAuth callback token
    const token = authAPI.handleOAuthCallback();
    if (token) {
      showMessage('Successfully logged in!', 'success');
    }
    
    // Check current user
    checkAuth();
    fetchLinks();
  }, []);

  const checkAuth = async () => {
    try {
      const user = await authAPI.getCurrentUser();
      setCurrentUser(user);
    } catch (error) {
      // User not authenticated - that's okay
      console.log('User not authenticated');
    }
  };

  const fetchLinks = async () => {
    try {
      setLoadingLinks(true);
      const data = await linksAPI.getLinks(0, 100, currentUser?.id);
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
      const results = await linksAPI.searchLinks(query, 10, 0.7, currentUser?.id);
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
    // Delete functionality not yet implemented in backend
    showMessage('Delete functionality coming soon!', 'info');
    
    // Uncomment when backend implements delete endpoint:
    /*
    try {
      await linksAPI.deleteLink(linkId);
      setLinks(prevLinks => prevLinks.filter(link => link._id !== linkId));
      showMessage('Link deleted successfully', 'success');
    } catch (error) {
      console.error('Error deleting link:', error);
      showMessage('Failed to delete link', 'error');
    }
    */
  };

  const handleLogin = () => {
    authAPI.googleLogin();
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      setCurrentUser(null);
      showMessage('Successfully logged out', 'success');
    } catch (error) {
      console.error('Error logging out:', error);
      showMessage('Failed to logout', 'error');
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
          <div className="header-right" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {currentUser ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.9rem', color: '#666' }}>Hello, {currentUser.name || currentUser.email}</span>
                <button 
                  onClick={handleLogout}
                  style={{ 
                    padding: '0.5rem 1rem', 
                    background: '#f44336', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '4px', 
                    cursor: 'pointer' 
                  }}
                >
                  Logout
                </button>
              </div>
            ) : (
              <button 
                onClick={handleLogin}
                style={{ 
                  padding: '0.5rem 1rem', 
                  background: '#4285f4', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '4px', 
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path fillRule="evenodd" clipRule="evenodd" d="M17.64 9.20454C17.64 8.56636 17.5827 7.95272 17.4764 7.36363H9V10.845H13.8436C13.635 11.97 13.0009 12.9231 12.0477 13.5613V15.8195H14.9564C16.6582 14.2527 17.64 11.9454 17.64 9.20454Z" fill="white"/>
                  <path fillRule="evenodd" clipRule="evenodd" d="M9 18C11.43 18 13.4673 17.1941 14.9564 15.8195L12.0477 13.5613C11.2418 14.1013 10.2109 14.4204 9 14.4204C6.65591 14.4204 4.67182 12.8372 3.96409 10.71H0.957275V13.0418C2.43818 15.9831 5.48182 18 9 18Z" fill="white"/>
                  <path fillRule="evenodd" clipRule="evenodd" d="M3.96409 10.71C3.78409 10.17 3.68182 9.59318 3.68182 9C3.68182 8.40682 3.78409 7.83 3.96409 7.29V4.95818H0.957273C0.347727 6.17318 0 7.54773 0 9C0 10.4523 0.347727 11.8268 0.957273 13.0418L3.96409 10.71Z" fill="white"/>
                  <path fillRule="evenodd" clipRule="evenodd" d="M9 3.57955C10.3214 3.57955 11.5077 4.03364 12.4405 4.92545L15.0218 2.34409C13.4632 0.891818 11.4259 0 9 0C5.48182 0 2.43818 2.01682 0.957275 4.95818L3.96409 7.29C4.67182 5.16273 6.65591 3.57955 9 3.57955Z" fill="white"/>
                </svg>
                Sign in with Google
              </button>
            )}
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