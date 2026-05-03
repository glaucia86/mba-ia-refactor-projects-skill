const settings = require('../config/settings');

function adminAuth(req, res, next) {
    if (!settings.adminToken) return next();

    const token = req.get('x-admin-token');
    if (token !== settings.adminToken) {
        return res.status(403).send('Forbidden');
    }

    return next();
}

module.exports = adminAuth;
