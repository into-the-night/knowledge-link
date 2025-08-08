import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import SearchBar from './SearchBar';
import LinkForm from './LinkForm';
import LinkList from './LinkList';
import SearchResults from './SearchResults';
import AddLinkModal from './AddLinkModal';
import LinksSidebar from './LinksSidebar';
import { fetchLinks, searchLinks, createLink } from '../api/links';
import './MainApp.css';

const MainApp = () => {
  const { user, logout } = useAuth();
  const [links, setLinks] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Fetch links on component mount
  useEffect(() => {
    loadLinks();
  }, []);

  const loadLinks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchLinks();
      setLinks(data);
    } catch (error) {
      console.error('Error fetching links:', error);
      setError('Failed to load links. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    if (!query.trim()) {
      setIsSearching(false);
      setSearchResults([]);
      setSearchQuery('');
      return;
    }

    setIsSearching(true);
    setSearchQuery(query);
    setLoading(true);
    setError(null);

    try {
      const results = await searchLinks(query);
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
      setError('Search failed. Please try again.');
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleLinkAdded = async (linkData) => {
    try {
      const newLink = await createLink(linkData);
      setLinks([newLink, ...links]);
      setIsModalOpen(false);
      // Show a success message
      const successMsg = document.createElement('div');
      successMsg.className = 'success-toast';
      successMsg.textContent = 'Link added successfully! Processing content...';
      document.body.appendChild(successMsg);
      setTimeout(() => successMsg.remove(), 3000);
    } catch (error) {
      console.error('Error adding link:', error);
      throw error; // Re-throw to let AddLinkModal handle the error
    }
  };

  const handleClearSearch = () => {
    setIsSearching(false);
    setSearchResults([]);
    setSearchQuery('');
  };

  return (
    <div className="main-app">
      <header className="app-header">
        <div className="header-left">
          <button 
            className="menu-button"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            aria-label="Toggle sidebar"
          >
            ☰
          </button>
          <h1 className="app-title">KnowledgeLink</h1>
        </div>
        <div className="header-center">
          <SearchBar onSearch={handleSearch} />
        </div>
        <div className="header-right">
          <button 
            className="add-link-button"
            onClick={() => setIsModalOpen(true)}
          >
            + Add Link
          </button>
          <div className="user-menu">
            <img 
              src={user?.picture || 'https://via.placeholder.com/40'} 
              alt={user?.name || 'User'} 
              className="user-avatar"
            />
            <div className="user-dropdown">
              <div className="user-info">
                <p className="user-name">{user?.name || 'User'}</p>
                <p className="user-email">{user?.email}</p>
              </div>
              <button onClick={logout} className="logout-button">
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="app-body">
        <LinksSidebar 
          links={links}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />
        
        <main className={`app-main ${isSidebarOpen ? 'with-sidebar' : ''}`}>
          {error && (
            <div className="error-message">
              {error}
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}

          {loading && (
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>Loading...</p>
            </div>
          )}

          {!loading && !isSearching && links.length === 0 && (
            <div className="empty-state">
              <h2>Welcome to KnowledgeLink!</h2>
              <p>Start by adding your first link using the button above.</p>
              <button 
                className="cta-button"
                onClick={() => setIsModalOpen(true)}
              >
                Add Your First Link
              </button>
            </div>
          )}

          {!loading && !isSearching && links.length > 0 && (
            <div className="links-section">
              <div className="section-header">
                <h2>Your Links</h2>
                <span className="link-count">{links.length} links saved</span>
              </div>
              <LinkList links={links} onLinksUpdate={loadLinks} />
            </div>
          )}

          {isSearching && (
            <div className="search-section">
              <div className="search-header">
                <h2>Search Results for "{searchQuery}"</h2>
                <button onClick={handleClearSearch} className="clear-search">
                  Clear Search
                </button>
              </div>
              {!loading && (
                <SearchResults 
                  results={searchResults} 
                  query={searchQuery}
                />
              )}
            </div>
          )}
        </main>
      </div>

      <AddLinkModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleLinkAdded}
      />
    </div>
  );
};

export default MainApp;
