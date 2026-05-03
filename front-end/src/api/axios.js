import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    const authTokens = localStorage.getItem('authTokens');
    if (authTokens) {
      const { access } = JSON.parse(authTokens);
      if (access) {
        config.headers.Authorization = `Bearer ${access}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Si l'erreur est 401 et qu'on n'a pas déjà essayé de rafraîchir
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const authTokens = localStorage.getItem('authTokens');
      if (authTokens) {
        try {
          const { refresh } = JSON.parse(authTokens);
          // Appel direct via axios pour ne pas déclencher les intercepteurs sur cette requête
          const response = await axios.post(`${API_URL}/api/auth/refresh/`, {
            refresh: refresh
          });
          
          if (response.status === 200) {
            // Mettre à jour les tokens dans le localStorage
            const newTokens = {
              access: response.data.access,
              refresh: response.data.refresh || refresh // Parfois refresh n'est pas retourné, on garde l'ancien
            };
            localStorage.setItem('authTokens', JSON.stringify(newTokens));
            
            // Rejouer la requête d'origine avec le nouveau token
            originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
            return axiosInstance(originalRequest);
          }
        } catch (refreshError) {
          // Si le refresh échoue (expired/invalide), on déconnecte l'utilisateur
          console.error("Refresh token failed", refreshError);
          localStorage.removeItem('authTokens');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // Pas de token existant, on redirige vers le login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
