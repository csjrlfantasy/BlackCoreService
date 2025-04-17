import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const RequireAuth = ({ children }) => {
  const navigate = useNavigate();

  useEffect(() => {
    if (!localStorage.getItem('authToken')) {
      navigate('/login', { replace: true });
    }
  }, [navigate]);

  return localStorage.getItem('authToken') ? children : null;
};