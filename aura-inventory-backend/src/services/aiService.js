const axios = require('axios');
const FLASK_URL = process.env.FLASK_URL;

// Get 90-day forecast from Flask
const callPredict = async () => {
  const resp = await axios.get(`${FLASK_URL}/predict`, { timeout: 60000 });
  return resp.data;
};

// Get optimization from Flask
const callOptimize = async () => {
  const resp = await axios.get(`${FLASK_URL}/optimize`, { timeout: 60000 });
  return resp.data;
};

module.exports = { callPredict, callOptimize };
