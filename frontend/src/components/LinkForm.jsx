import { useState } from 'react';
import './LinkForm.css';

const LinkForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    url: '',
    title: '',
    description: '',
    tags: ''
  });

  const [errors, setErrors] = useState({});

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
      // Reset form on success
      setFormData({
        url: '',
        title: '',
        description: '',
        tags: ''
      });
      setErrors({});
    } catch (error) {
      setErrors({ submit: error.message || 'Failed to save link' });
    }
  };

  return (
    <form className="link-form" onSubmit={handleSubmit}>
      <h2>Save a New Link</h2>
      
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
        />
        {errors.url && <span className="error-message">{errors.url}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="title">Title (optional)</label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          placeholder="Page title (will be auto-fetched if not provided)"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Description (optional)</label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Brief description (will be auto-fetched if not provided)"
          rows="3"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="tags">Tags (optional)</label>
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

      <button type="submit" disabled={loading} className="submit-btn">
        {loading ? 'Saving...' : 'Save Link'}
      </button>
    </form>
  );
};

export default LinkForm;
