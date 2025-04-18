import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaPaperPlane, FaRobot, FaUserAlt, FaPills, FaFlask, FaShieldAlt, FaAppleAlt, FaExclamationTriangle, FaWifi, FaInfoCircle, FaExclamationCircle } from 'react-icons/fa';

const SymptomChecker = () => {
  const [messages, setMessages] = useState([
    { 
      text: "Hello! I'm AI Sahayak. Please describe your symptoms in English or Hinglish, and I'll try to help you.", 
      isBot: true 
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState(null);
  const [serverStatus, setServerStatus] = useState('unknown'); // 'online', 'offline', 'unknown'

  // Check if the server is running
  useEffect(() => {
    checkServerStatus();
  }, []);

  const checkServerStatus = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        setServerStatus('online');
        const data = await response.json();
        console.log('Server is online:', data);
      } else {
        setServerStatus('offline');
      }
    } catch (error) {
      console.error('Server status check failed:', error);
      setServerStatus('offline');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;
    
    // Add user message
    const userMessage = { text: inputValue, isBot: false };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    
    // Set loading state
    setIsLoading(true);
    
    // If server is offline, show error immediately
    if (serverStatus === 'offline') {
      const errorMessage = { 
        text: "The diagnosis server appears to be offline. Please make sure your backend is running on http://127.0.0.1:8000",
        isBot: true 
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
      return;
    }
    
    try {
      // Make API call to the diagnose endpoint
      console.log('Sending symptoms:', inputValue);
      
      const response = await fetch('http://127.0.0.1:8000/diagnose', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ symptoms: inputValue }),
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} - ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Diagnosis response:', data);
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      setDiagnosis(data);
      
      // Format and add bot response based on AI suggestion from backend
      const botMessage = { 
        text: data.ai_suggestion || `Based on your symptoms, you might have ${data.disease}.`,
        isBot: true 
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      
      // Add specific error message
      let errorText = "Sorry, I couldn't process your symptoms right now.";
      
      if (error.message.includes('Failed to fetch') || error.name === 'TypeError') {
        errorText = "Unable to connect to the diagnosis server. Please ensure your backend is running on http://127.0.0.1:8000";
        setServerStatus('offline');
      } else if (error.message.includes('CORS')) {
        errorText = "There's a CORS issue connecting to the server. Please check your backend configuration.";
      } else if (error.message.includes('Gemini API Error')) {
        errorText = "There was an issue with the Gemini AI service. Please try again later.";
      } else {
        errorText = `Error: ${error.message}`;
      }
      
      const errorMessage = { 
        text: errorText,
        isBot: true 
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const retryConnection = async () => {
    await checkServerStatus();
    const statusMessage = { 
      text: serverStatus === 'online' 
        ? "Successfully connected to the diagnosis server! You can now describe your symptoms." 
        : "Still unable to connect to the server. Please check that your backend is running.",
      isBot: true 
    };
    setMessages(prev => [...prev, statusMessage]);
  };

  return (
    <div className="symptom-checker">
      <motion.h1 
        className="title glow-text"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <span className="highlight">Symptom</span> Checker
      </motion.h1>
      
      {serverStatus === 'offline' && (
        <motion.div 
          className="server-status-warning"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <FaWifi /> The diagnosis server appears to be offline. 
          <button onClick={retryConnection} className="retry-button">Retry Connection</button>
        </motion.div>
      )}
      
      <div className="chat-container">
        <div className="chat-messages">
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={index}
                className={`message ${message.isBot ? 'bot' : 'user'}`}
                initial={{ opacity: 0, x: message.isBot ? -20 : 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="message-icon">
                  {message.isBot ? <FaRobot /> : <FaUserAlt />}
                </div>
                <div className="message-text">
                  {message.text}
                </div>
              </motion.div>
            ))}
            
            {isLoading && (
              <motion.div
                className="message bot"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="message-icon">
                  <FaRobot />
                </div>
                <div className="message-text typing">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        <form className="chat-input" onSubmit={handleSendMessage}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Describe your symptoms in English or Hinglish..."
            disabled={isLoading || serverStatus === 'offline'}
          />
          <motion.button
            type="submit"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={isLoading || !inputValue.trim() || serverStatus === 'offline'}
          >
            <FaPaperPlane />
          </motion.button>
        </form>
      </div>
      
      {diagnosis && (
        <motion.div
          className="diagnosis-results"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* AI Suggestion Banner */}
          <motion.div 
            className="ai-suggestion-banner"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            <div dangerouslySetInnerHTML={{ __html: diagnosis.ai_suggestion.replace(/\*([^*]+)\*/, '<strong>$1</strong>') }} />
          </motion.div>
          
          {/* Disease Name Header */}
          <motion.h2 
            className="disease-name-header"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <span className="highlight">{diagnosis.disease}</span> Details
          </motion.h2>
          
          {/* Alert if present */}
          {diagnosis.alert && (
            <motion.div 
              className="alert-box"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <FaExclamationTriangle /> {diagnosis.alert}
            </motion.div>
          )}
          
          {/* Emergency Status Indicator */}
          <motion.div 
            className={`emergency-status ${diagnosis.emergency ? 'emergency' : 'non-emergency'}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            {diagnosis.emergency ? 
              <><FaExclamationCircle /> Critical condition requiring immediate medical attention</> : 
              <><FaInfoCircle /> Non-critical condition, but medical consultation is recommended</>
            }
          </motion.div>
          
          {/* Diagnosis Description */}
          <motion.div 
            className="diagnosis-description"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <h3><FaInfoCircle /> About {diagnosis.disease}</h3>
            <p><strong>Diagnosis:</strong> {diagnosis.diagnosis}</p>
          </motion.div>
          
          {/* Details Grid */}
          <div className="details-grid">
            {/* Medicines Card */}
            <motion.div 
              className="detail-card medicines"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <h3><FaPills /> Recommended Medicines</h3>
              <ul>
                {diagnosis.medicines && diagnosis.medicines.map((medicine, index) => (
                  <li key={`med-${index}`}>{medicine}</li>
                ))}
                {(!diagnosis.medicines || diagnosis.medicines.length === 0) && (
                  <li className="no-data">No specific medicines recommended</li>
                )}
              </ul>
            </motion.div>
            
            {/* Tests Card */}
            <motion.div 
              className="detail-card tests"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              <h3><FaFlask /> Suggested Tests</h3>
              <ul>
                {diagnosis.tests && diagnosis.tests.map((test, index) => (
                  <li key={`test-${index}`}>{test}</li>
                ))}
                {(!diagnosis.tests || diagnosis.tests.length === 0) && (
                  <li className="no-data">No specific tests recommended</li>
                )}
              </ul>
            </motion.div>
            
            {/* Precautions Card */}
            <motion.div 
              className="detail-card precautions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
            >
              <h3><FaShieldAlt /> Precautions</h3>
              <ul>
                {diagnosis.precautions && diagnosis.precautions.map((precaution, index) => (
                  <li key={`precaution-${index}`}>{precaution}</li>
                ))}
                {(!diagnosis.precautions || diagnosis.precautions.length === 0) && (
                  <li className="no-data">No specific precautions recommended</li>
                )}
              </ul>
            </motion.div>
            
            {/* Food Card */}
            <motion.div 
              className="detail-card food"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
            >
              <h3><FaAppleAlt /> Recommended Diet</h3>
              <ul>
                {diagnosis.food && diagnosis.food.map((food, index) => (
                  <li key={`food-${index}`}>{food}</li>
                ))}
                {(!diagnosis.food || diagnosis.food.length === 0) && (
                  <li className="no-data">No specific dietary recommendations</li>
                )}
              </ul>
            </motion.div>
          </div>
          
          {/* Disclaimer */}
          <motion.div 
            className="disclaimer"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.0 }}
          >
            <strong>Disclaimer:</strong> This is an AI-powered analysis and should not replace professional medical advice. 
            Please consult with a healthcare provider.
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default SymptomChecker; 