import React from 'react';
import { useAuth } from '../context/AuthContext';
import './LandingPage.css';

const LandingPage = () => {
  const { login } = useAuth();

  return (
    <div className="landing-page">
      <header className="landing-header">
        <div className="logo">
          <h1>KnowledgeLink</h1>
        </div>
      </header>

      <main className="landing-main">
        <section className="hero">
          <div className="hero-content">
            <h2 className="hero-title">
              Your Personal Knowledge Repository
            </h2>
            <p className="hero-subtitle">
              Save, organize, and search through your web links with AI-powered summarization
            </p>
            <button onClick={login} className="cta-button">
              <svg className="google-icon" viewBox="0 0 24 24" width="20" height="20">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Sign in with Google
            </button>
          </div>
        </section>

        <section className="features">
          <h3 className="features-title">Features</h3>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔗</div>
              <h4>Save Links</h4>
              <p>Quickly save any web link with automatic metadata extraction</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h4>AI Summaries</h4>
              <p>Get intelligent summaries of your saved content</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h4>Smart Search</h4>
              <p>Find exactly what you need with semantic search</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📚</div>
              <h4>Organize</h4>
              <p>Keep your knowledge organized and accessible</p>
            </div>
          </div>
        </section>

        <section className="how-it-works">
          <h3 className="section-title">How It Works</h3>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h4>Save Links</h4>
                <p>Add any web link to your personal library</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h4>AI Processing</h4>
                <p>Our AI analyzes and summarizes the content</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h4>Search & Discover</h4>
                <p>Find information instantly with semantic search</p>
              </div>
            </div>
          </div>
        </section>

        <section className="cta-section">
          <h3>Ready to Get Started?</h3>
          <p>Join KnowledgeLink and start building your personal knowledge base today</p>
          <button onClick={login} className="cta-button secondary">
            Get Started Free
          </button>
        </section>
      </main>

      <footer className="landing-footer">
        <p>&copy; 2024 KnowledgeLink. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
