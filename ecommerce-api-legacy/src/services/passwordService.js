const crypto = require('crypto');

function createPasswordHash(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(password, salt, 32).toString('hex');

    return `scrypt$${salt}$${hash}`;
}

module.exports = { createPasswordHash };
