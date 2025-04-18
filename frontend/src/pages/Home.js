import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaImage, FaCommentMedical, FaArrowRight, FaCheck, FaCrown, FaRegUser, FaBuilding } from 'react-icons/fa';
import Image from '../assets/landingpage_illustration.png';

const Home = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { 
        staggerChildren: 0.2,
        duration: 0.5 
      }
    }
  };

  const itemVariants = {
    hidden: { y: 50, opacity: 0 },
    visible: { 
      y: 0, 
      opacity: 1,
      transition: { duration: 0.5 }
    }
  };

  // Load Razorpay script
  useEffect(() => {
    const loadRazorpayScript = () => {
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.async = true;
      document.body.appendChild(script);
    };
    loadRazorpayScript();

    return () => {
      // Cleanup
      const script = document.querySelector('script[src="https://checkout.razorpay.com/v1/checkout.js"]');
      if (script) {
        document.body.removeChild(script);
      }
    };
  }, []);

  // Function to handle payment
  const handlePayment = (amount, planName) => {
    if (window.Razorpay) {
      const options = {
        key: 'rzp_test_hxp0wE0y7KdXKr', // Using the provided Razorpay test key
        amount: amount * 100, // Amount in paise
        currency: 'INR',
        name: 'AI Sahayak',
        description: `Subscription for ${planName} Plan`,
        image: 'https://i.imgur.com/3g7nmJC.png', // Replace with your logo
        handler: function(response) {
          alert(`Payment successful! Payment ID: ${response.razorpay_payment_id}`);
        },
        prefill: {
          name: 'Your Name',
          email: 'your.email@example.com',
          contact: '9999999999',
        },
        theme: {
          color: '#0077cc',
        },
      };

      const razorpayInstance = new window.Razorpay(options);
      razorpayInstance.open();
    } else {
      alert('Razorpay SDK failed to load. Please check your connection.');
    }
  };

  const features = [
    {
      id: 1,
      title: 'Disease Image Analysis',
      description: 'Upload medical images for AI analysis to detect potential diseases and get detailed information.',
      icon: <FaImage />,
      path: '/image-analysis',
      color: '#4db6ff'
    },
    {
      id: 2,
      title: 'Symptom Checker',
      description: 'Describe your symptoms to our AI and receive potential causes and recommendations.',
      icon: <FaCommentMedical />,
      path: '/symptom-checker',
      color: '#00cc99'
    }
  ];

  const subscriptionPlans = [
    {
      id: 1,
      name: 'Basic',
      price: 499,
      duration: 'per month',
      icon: <FaRegUser />,
      color: '#4db6ff',
      features: [
        'Basic Health Analysis',
        'Symptom Checker (5 checks/day)',
        'Limited Image Analysis',
        'Email Support'
      ]
    },
    {
      id: 2,
      name: 'Premium',
      price: 999,
      duration: 'per month',
      icon: <FaCrown />,
      color: '#f59e0b',
      isFeatured: true,
      features: [
        'Advanced Health Analysis',
        'Unlimited Symptom Checks',
        'Unlimited Image Analysis',
        'Priority Email Support',
        'Detailed Health Reports'
      ]
    },
    {
      id: 3,
      name: 'Enterprise',
      price: 4999,
      duration: 'per month',
      icon: <FaBuilding />,
      color: '#10b981',
      features: [
        'Everything in Premium',
        'Multi-user Access',
        'API Access',
        'Dedicated Support',
        'Custom Integrations',
        'Training Sessions'
      ]
    }
  ];

  return (
    <div className="home-page">
      <section className="hero-section">
        <motion.div 
          className="hero-content"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <motion.h1
            initial={{ y: -30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
            className="hero-title"
          >
            <span className="highlight">AI Sahayak</span> <br />
            Your Health Assistant
          </motion.h1>
          <motion.p
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="hero-subtitle"
          >
            Advanced AI solutions to help you understand health conditions through image analysis and symptom checking.
          </motion.p>
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="hero-buttons"
          >
            <Link to="/image-analysis" className="button primary">
              Analyze Image <FaArrowRight />
            </Link>
            <Link to="/symptom-checker" className="button secondary">
              Check Symptoms <FaArrowRight />
            </Link>
          </motion.div>
        </motion.div>
        <div className="hero-image">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.8 }}
            className="image-container"
          >
            {/* Use the imported image instead of placeholder */}
            <img src={Image} alt="Medical AI Illustration" className="hero-image-content" />
          </motion.div>
        </div>
      </section>

      <section className="features-section">
        <motion.h2
          className="section-title"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          Our <span className="highlight">Features</span>
        </motion.h2>
        
        <motion.div 
          className="features-grid"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {features.map((feature) => (
            <motion.div 
              key={feature.id}
              className="feature-card"
              variants={itemVariants}
            >
              <div className="feature-icon" style={{ backgroundColor: feature.color }}>
                {feature.icon}
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
              <Link to={feature.path} className="feature-link">
                Try Now <FaArrowRight />
              </Link>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* New Subscription Section */}
      <section className="subscription-section">
        <motion.h2
          className="section-title"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
        >
          Choose Your <span className="highlight">Plan</span>
        </motion.h2>
        
        <motion.div 
          className="subscription-grid"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          {subscriptionPlans.map((plan) => (
            <motion.div 
              key={plan.id}
              className={`subscription-card ${plan.isFeatured ? 'featured' : ''}`}
              variants={itemVariants}
            >
              {plan.isFeatured && <div className="popular-badge">Most Popular</div>}
              <div className="plan-icon" style={{ backgroundColor: plan.color }}>
                {plan.icon}
              </div>
              <h3 className="plan-name">{plan.name}</h3>
              <div className="plan-price">
                <span className="price-amount">₹{plan.price}</span>
                <span className="price-duration">{plan.duration}</span>
              </div>
              <ul className="plan-features">
                {plan.features.map((feature, index) => (
                  <li key={index}>
                    <FaCheck className="feature-check" /> {feature}
                  </li>
                ))}
              </ul>
              <button 
                className="pay-button"
                onClick={() => handlePayment(plan.price, plan.name)}
              >
                Subscribe Now
              </button>
            </motion.div>
          ))}
        </motion.div>
      </section>

      <section className="about-section">
        <motion.div
          className="about-content"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="section-title">About <span className="highlight">AI Sahayak</span></h2>
          <p className="about-text">
            AI Sahayak is your advanced health assistant powered by artificial intelligence. Our platform
            provides tools for disease detection through image analysis and a symptom checker to help you
            understand potential health conditions. We combine cutting-edge AI technology with medical knowledge
            to provide informative health insights.
          </p>
          <p className="about-text disclaimer">
            <strong>Disclaimer:</strong> AI Sahayak is designed for informational purposes only and is not a substitute
            for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other
            qualified health provider with any questions you may have regarding a medical condition.
          </p>
        </motion.div>
      </section>
    </div>
  );
};

export default Home; 