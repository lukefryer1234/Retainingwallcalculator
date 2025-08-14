import axios from 'axios';

// It's good practice to set a base URL for the API.
// During development, the React app and Django backend run on different ports,
// so we'll need to configure proxying or use the full URL.
// For development, we'll use the full Django server URL.
// NOTE: This will need to be configured properly for production.
const API_URL = 'http://127.0.0.1:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getSoilTypes = () => {
  return apiClient.get('/soil-types/');
};

export const getSurchargeLoads = () => {
  return apiClient.get('/surcharge-loads/');
};

export const postCalculation = (data) => {
  return apiClient.post('/calculate/', data);
};
