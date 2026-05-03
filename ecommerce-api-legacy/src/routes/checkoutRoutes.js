const express = require('express');
const CheckoutController = require('../controllers/checkoutController');
const asyncHandler = require('../middlewares/asyncHandler');

function checkoutRoutes(db) {
    const router = express.Router();
    const controller = new CheckoutController(db);

    router.post('/api/checkout', asyncHandler(controller.checkout));

    return router;
}

module.exports = checkoutRoutes;
