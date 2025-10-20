const { callPredict, callOptimize } = require('../services/aiService');

// GET /api/predict
exports.predict = async (req, res, next) => {
  try {
    const prediction = await callPredict();
    res.json({ success: true, forecast: prediction.forecast });
  } catch (err) {
    next(err);
  }
};

// GET /api/optimize
exports.optimize = async (req, res, next) => {
  try {
    const optimization = await callOptimize();
    res.json({ success: true, optimization });
  } catch (err) {
    next(err);
  }
};
