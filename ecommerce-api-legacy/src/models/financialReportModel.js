const { all } = require('../database/connection');

class FinancialReportModel {
    constructor(db) {
        this.db = db;
    }

    async listCourseRevenue() {
        const rows = await all(this.db, `
            SELECT
                c.id AS course_id,
                c.title AS course_title,
                e.id AS enrollment_id,
                u.name AS student_name,
                p.amount AS payment_amount,
                p.status AS payment_status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            ORDER BY c.id, e.id
        `);

        const coursesById = new Map();

        rows.forEach((row) => {
            let course = coursesById.get(row.course_id);
            if (!course) {
                course = { course: row.course_title, revenue: 0, students: [] };
                coursesById.set(row.course_id, course);
            }

            if (row.enrollment_id) {
                if (row.payment_status === 'PAID') {
                    course.revenue += row.payment_amount;
                }

                course.students.push({
                    student: row.student_name || 'Unknown',
                    paid: row.payment_amount || 0
                });
            }
        });

        return Array.from(coursesById.values());
    }
}

module.exports = FinancialReportModel;
