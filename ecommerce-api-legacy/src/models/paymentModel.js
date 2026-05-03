const { run } = require('../database/connection');

class PaymentModel {
    constructor(db) {
        this.db = db;
    }

    create(payment) {
        return run(this.db, 'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [
            payment.enrollmentId,
            payment.amount,
            payment.status
        ]);
    }
}

module.exports = PaymentModel;
