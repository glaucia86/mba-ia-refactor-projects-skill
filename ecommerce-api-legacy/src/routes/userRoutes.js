const express = require('express');
const UserController = require('../controllers/userController');
const adminAuth = require('../middlewares/adminAuth');
const asyncHandler = require('../middlewares/asyncHandler');

function userRoutes(db) {
    const router = express.Router();
    const controller = new UserController(db);

    router.delete('/api/users/:id', adminAuth, asyncHandler(controller.delete));

    return router;
}

module.exports = userRoutes;
