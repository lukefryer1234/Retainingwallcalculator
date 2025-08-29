import axios from 'axios';

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

export const getWallMaterials = () => {
  return apiClient.get('/wall-materials/');
};

export const getSurchargeLoads = () => {
  return apiClient.get('/surcharge-loads/');
};

export const postCalculation = (data) => {
  return apiClient.post('/calculate/', data);
};

export const generatePDF = (data) => {
  return apiClient.post('/generate-pdf/', data, {
    responseType: 'blob', // Important for handling file downloads
  });
};
