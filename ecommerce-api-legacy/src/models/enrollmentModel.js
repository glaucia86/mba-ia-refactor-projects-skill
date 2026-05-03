const { run } = require('../database/connection');

class EnrollmentModel {
    constructor(db) {
        this.db = db;
    }

    create(enrollment) {
        return run(this.db, 'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [
            enrollment.userId,
            enrollment.courseId
        ]);
    }
}

module.exports = EnrollmentModel;
