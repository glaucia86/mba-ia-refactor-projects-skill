const express = require('express');
const AdminController = require('../controllers/adminController');
const adminAuth = require('../middlewares/adminAuth');
const asyncHandler = require('../middlewares/asyncHandler');

function adminRoutes(db) {
    const router = express.Router();
    const controller = new AdminController(db);

    router.get('/api/admin/financial-report', adminAuth, asyncHandler(controller.financialReport));

    return router;
}

module.exports = adminRoutes;
