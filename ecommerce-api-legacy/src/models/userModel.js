const { get, run } = require('../database/connection');

class UserModel {
    constructor(db) {
        this.db = db;
    }

    findByEmail(email) {
        return get(this.db, 'SELECT id, name, email FROM users WHERE email = ?', [email]);
    }

    create(user) {
        return run(this.db, 'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
            user.name,
            user.email,
            user.passwordHash
        ]);
    }

    deleteById(id) {
        return run(this.db, 'DELETE FROM users WHERE id = ?', [id]);
    }
}

module.exports = UserModel;
