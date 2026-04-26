import React, { createContext, useState, useEffect } from 'react';
import axiosInstance from '../api/axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      const authTokens = localStorage.getItem('authTokens');
      if (authTokens) {
        try {
          // Verify token and fetch user profile
          const response = await axiosInstance.get('/api/auth/profile/');
          setUser(response.data);
        } catch (error) {
          console.error("Error fetching user profile:", error);
          // Token is invalid or expired, interceptor handles clearing localStorage if necessary
          setUser(null);
        }
      }
      setLoading(false);
    };

    fetchUser();
  }, []);

  const loginUser = async (username, password) => {
    try {
      const response = await axiosInstance.post('/api/auth/login/', {
        username,
        password,
      });

      if (response.data && response.data.access) {
        localStorage.setItem('authTokens', JSON.stringify(response.data));
        // After login, fetch the profile
        const profileRes = await axiosInstance.get('/api/auth/profile/', {
          headers: {
            Authorization: `Bearer ${response.data.access}`
          }
        });
        setUser(profileRes.data);
        return true;
      }
      return false;
    } catch (error) {
      console.error("Login Error:", error);
      throw error;
    }
  };

  const logoutUser = () => {
    localStorage.removeItem('authTokens');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loginUser, logoutUser, loading }}>
      {!loading ? children : <div className="d-flex justify-content-center mt-5"><div className="spinner-border text-success" role="status"><span className="visually-hidden">Loading...</span></div></div>}
    </AuthContext.Provider>
  );
};
