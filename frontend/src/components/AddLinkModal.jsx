import { useState, useEffect } from 'react';
import './AddLinkModal.css';

const AddLinkModal = ({ isOpen, onClose, onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    url: '',
    title: '',
    description: '',
    tags: ''
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (!isOpen) {
      // Reset form when modal closes
      setFormData({
        url: '',
        title: '',
        description: '',
        tags: ''
      });
      setErrors({});
    }
  }, [isOpen]);

  const validateUrl = (url) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate
    const newErrors = {};
    if (!formData.url.trim()) {
      newErrors.url = 'URL is required';
    } else if (!validateUrl(formData.url)) {
      newErrors.url = 'Please enter a valid URL';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Process tags
    const processedData = {
      ...formData,
      tags: formData.tags
        ? formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
        : []
    };

    // Remove empty optional fields
    if (!processedData.title) delete processedData.title;
    if (!processedData.description) delete processedData.description;

    try {
      await onSubmit(processedData);
      onClose(); // Close modal on success
    } catch (error) {
      setErrors({ submit: error.message || 'Failed to save link' });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add New Link</h2>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18" strokeWidth="2" strokeLinecap="round"/>
              <line x1="6" y1="6" x2="18" y2="18" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        <form className="modal-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="url">URL *</label>
            <input
              type="text"
              id="url"
              name="url"
              value={formData.url}
              onChange={handleChange}
              placeholder="https://example.com"
              className={errors.url ? 'error' : ''}
              disabled={loading}
              autoFocus
            />
            {errors.url && <span className="error-message">{errors.url}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="title">Title</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="Optional - will be auto-fetched if not provided"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Optional - will be auto-fetched if not provided"
              rows="3"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="tags">Tags</label>
            <input
              type="text"
              id="tags"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              placeholder="tag1, tag2, tag3 (comma-separated)"
              disabled={loading}
            />
          </div>

          {errors.submit && (
            <div className="error-message submit-error">{errors.submit}</div>
          )}

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Saving...' : 'Save Link'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddLinkModal;
