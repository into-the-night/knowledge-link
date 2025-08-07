import { useState, useEffect } from 'react';
import LinkForm from './components/LinkForm';
import LinkList from './components/LinkList';
import linksAPI from './api/links';
import './App.css';

function App() {
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingLinks, setLoadingLinks] = useState(true);
  const [message, setMessage] = useState(null);

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

  const handleSubmit = async (linkData) => {
    try {
      setLoading(true);
      const newLink = await linksAPI.createLink(linkData);
      setLinks(prevLinks => [newLink, ...prevLinks]);
      showMessage('Link saved successfully!', 'success');
    } catch (error) {
      console.error('Error saving link:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (linkId) => {
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

  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1>🔗 KnowledgeLink</h1>
          <p>Your Personal Knowledge Base</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {message && (
            <div className={`message ${message.type}`}>
              {message.text}
            </div>
          )}

          <LinkForm onSubmit={handleSubmit} loading={loading} />
          
          <LinkList 
            links={links} 
            onDelete={handleDelete}
            loading={loadingLinks}
          />
        </div>
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>© 2024 KnowledgeLink. Save, organize, and search your knowledge.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;