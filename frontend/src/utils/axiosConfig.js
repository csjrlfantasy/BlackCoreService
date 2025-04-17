import axios from 'axios';

const instance = axios.create({
  baseURL: '/api', // 添加统一API前缀
  timeout: 10000,
});

instance.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default instance;