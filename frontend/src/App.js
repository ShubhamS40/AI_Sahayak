import React, { useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { motion } from "framer-motion";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import ImageAnalysisPage from "./pages/ImageAnalysisPage";
import SymptomCheckerPage from "./pages/SymptomCheckerPage";
import "./style.css"; // Import External CSS File

const App = () => {
  useEffect(() => {
    // Set dark theme class on body
    document.body.classList.add('dark-theme');
    
    // Cleanup
    return () => {
      document.body.classList.remove('dark-theme');
    };
  }, []);

  return (
    <Router>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="app"
      >
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/image-analysis" element={<ImageAnalysisPage />} />
            <Route path="/symptom-checker" element={<SymptomCheckerPage />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>&copy; {new Date().getFullYear()} AI Sahayak. All rights reserved.</p>
        </footer>
      </motion.div>
    </Router>
  );
};

export default App;
