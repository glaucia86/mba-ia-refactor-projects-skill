const AppError = require('../errors/AppError');
const UserModel = require('../models/userModel');
const CourseModel = require('../models/courseModel');
const EnrollmentModel = require('../models/enrollmentModel');
const PaymentModel = require('../models/paymentModel');
const AuditLogModel = require('../models/auditLogModel');
const { run } = require('../database/connection');
const { createPasswordHash } = require('./passwordService');
const { PaymentStatus, processPayment } = require('./paymentService');
const cacheService = require('./cacheService');

class CheckoutService {
    constructor(db) {
        this.db = db;
        this.users = new UserModel(db);
        this.courses = new CourseModel(db);
        this.enrollments = new EnrollmentModel(db);
        this.payments = new PaymentModel(db);
        this.auditLogs = new AuditLogModel(db);
    }

    async checkout(body) {
        const input = this.normalizeInput(body);
        const course = await this.courses.findActiveById(input.courseId);
        if (!course) throw new AppError(404, 'Curso não encontrado');

        const status = processPayment(input.cardNumber);
        if (status === PaymentStatus.DENIED) throw new AppError(400, 'Pagamento recusado');

        await run(this.db, 'BEGIN');
        try {
            let user = await this.users.findByEmail(input.email);
            if (!user) {
                if (!input.password) throw new AppError(400, 'Bad Request');
                const createdUser = await this.users.create({
                    name: input.name,
                    email: input.email,
                    passwordHash: createPasswordHash(input.password)
                });
                user = { id: createdUser.lastID };
            }

            const enrollment = await this.enrollments.create({ userId: user.id, courseId: course.id });
            await this.payments.create({
                enrollmentId: enrollment.lastID,
                amount: course.price,
                status
            });
            await this.auditLogs.create(`Checkout curso ${course.id} por ${user.id}`);

            await run(this.db, 'COMMIT');

            cacheService.save(`last_checkout_${user.id}`, course.title);

            return { msg: 'Sucesso', enrollment_id: enrollment.lastID };
        } catch (err) {
            await run(this.db, 'ROLLBACK');
            throw err;
        }
    }

    normalizeInput(body) {
        const courseId = Number(body.courseId ?? body.c_id);
        const input = {
            name: body.name ?? body.usr,
            email: body.email ?? body.eml,
            password: body.password ?? body.pwd,
            courseId,
            cardNumber: body.cardNumber ?? body.card
        };

        if (!input.name || !input.email || !Number.isInteger(courseId) || !input.cardNumber) {
            throw new AppError(400, 'Bad Request');
        }

        return input;
    }
}

module.exports = CheckoutService;
