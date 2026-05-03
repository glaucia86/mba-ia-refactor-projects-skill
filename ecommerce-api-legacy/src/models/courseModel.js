const { get } = require('../database/connection');

class CourseModel {
    constructor(db) {
        this.db = db;
    }

    findActiveById(id) {
        return get(this.db, 'SELECT id, title, price FROM courses WHERE id = ? AND active = 1', [id]);
    }
}

module.exports = CourseModel;
