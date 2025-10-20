const express = require('express');
const router = express.Router();
const { predict, optimize } = require('../controllers/aiController');

router.get('/predict', predict);    // get 90-day forecast
router.get('/optimize', optimize);  // get optimal reorder plan

module.exports = router;
