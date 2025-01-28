const config = {
  apiUrl: process.env.NODE_ENV === 'production' 
    ? 'https://btc-predictor-backend.onrender.com'
    : 'http://localhost:10000'
};

export default config; 