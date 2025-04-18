import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaCloudUploadAlt, FaSearch, FaInfoCircle, FaPills, FaExclamationTriangle, FaShieldAlt } from "react-icons/fa";

const ImageDiseasesAnalyzer = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Animations configuration
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { duration: 0.5 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { 
      y: 0, 
      opacity: 1,
      transition: { duration: 0.5 }
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setError(null);

    // Generate Preview
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return alert("Please select a file first.");
    
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://localhost:8000/predict", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      setPrediction(data);
    } catch (error) {
      console.error("Error:", error);
      setError("Failed to analyze image. Please try again or check your connection.");
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      className="container"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.h1 
        className="title glow-text"
        variants={itemVariants}
      >
        <span className="highlight">AI Sahayak</span> - Disease Detection
      </motion.h1>

      <motion.div 
        className="upload-section"
        variants={itemVariants}
      >
        <label className="file-input-label">
          <input 
            type="file" 
            onChange={handleFileChange} 
            className="file-input"
            accept="image/*"
          />
          <FaCloudUploadAlt className="upload-icon" />
          <span>Choose a medical image</span>
        </label>
        
        <AnimatePresence>
          {previewUrl && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="preview-container"
            >
              <img src={previewUrl} alt="Preview" className="image-preview" />
            </motion.div>
          )}
        </AnimatePresence>
        
        <motion.button 
          onClick={handleUpload}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          disabled={loading || !selectedFile}
          className="predict-button"
        >
          {loading ? (
            <span className="loading-spinner"></span>
          ) : (
            <>
              <FaSearch className="button-icon" /> Analyze Image
            </>
          )}
        </motion.button>
        
        {error && (
          <motion.div 
            className="error-message"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <FaExclamationTriangle /> {error}
          </motion.div>
        )}
      </motion.div>

      <AnimatePresence>
        {prediction && (
          <motion.div 
            className="result-container"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            transition={{ duration: 0.5 }}
          >
            <motion.div 
              className="result-header"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <FaInfoCircle className="result-icon" />
              <h2 className="disease-title">
                <span className="highlight">{prediction.predicted_disease}</span> Detected
              </h2>
            </motion.div>
            
            {prediction.confidence && (
              <motion.div 
                className="confidence-container"
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "100%" }}
                transition={{ delay: 0.3, duration: 0.8 }}
              >
                <div className="confidence-label">AI Confidence Level:</div>
                <div className="confidence-bar-container">
                  <div 
                    className="confidence-bar" 
                    style={{ width: `${prediction.confidence}%` }}
                  ></div>
                </div>
                <div className="confidence-percentage">{prediction.confidence}%</div>
              </motion.div>
            )}
            
            <div className="result-cards-grid">
              {/* Disease Information Card */}
              <motion.div 
                className="result-card info-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <div className="card-header">
                  <FaInfoCircle className="card-icon" />
                  <h3>Disease Information</h3>
                </div>
                <div className="card-content" dangerouslySetInnerHTML={{ __html: prediction.disease_info }} />
              </motion.div>
              
              {/* Treatment Card */}
              {prediction.treatment && (
                <motion.div 
                  className="result-card treatment-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <div className="card-header">
                    <FaPills className="card-icon" />
                    <h3>Recommended Treatment</h3>
                  </div>
                  <div className="card-content" dangerouslySetInnerHTML={{ __html: prediction.treatment }} />
                </motion.div>
              )}
              
              {/* Prevention Card */}
              {prediction.prevention && (
                <motion.div 
                  className="result-card prevention-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                >
                  <div className="card-header">
                    <FaShieldAlt className="card-icon" />
                    <h3>Prevention</h3>
                  </div>
                  <div className="card-content" dangerouslySetInnerHTML={{ __html: prediction.prevention }} />
                </motion.div>
              )}
            </div>
            
            <motion.div 
              className="disclaimer-box"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
            >
              <FaExclamationTriangle className="disclaimer-icon" />
              <p><strong>Medical Disclaimer:</strong> This is an AI-assisted prediction and should not replace professional medical diagnosis. 
              Please consult with a healthcare provider for proper evaluation and treatment.</p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ImageDiseasesAnalyzer; 