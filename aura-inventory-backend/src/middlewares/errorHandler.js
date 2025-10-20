const errorHandler = (err, req, res, next) => {
  console.error(err.stack || err);
  const status = err.response?.status || 500;
  const message = err.response?.data?.message || err.message || 'Server error';
  res.status(status).json({ success: false, message });
};

module.exports = { errorHandler };
