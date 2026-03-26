import React from 'react';
import { useNavigate } from 'react-router-dom';
import './App.css';

const Success = () => {
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div className="success-container">
      <h1>Login Successful!</h1>
      <p>Welcome to the Employee Management System.</p>
      <button onClick={handleGoHome} className="success-btn">Go to Home</button>
    </div>
  );
};

export default Success;
