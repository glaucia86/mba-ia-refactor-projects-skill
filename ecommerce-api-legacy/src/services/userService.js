const AppError = require('../errors/AppError');
const UserModel = require('../models/userModel');

class UserService {
    constructor(db) {
        this.users = new UserModel(db);
    }

    async deleteUser(id) {
        const userId = Number(id);
        if (!Number.isInteger(userId)) throw new AppError(400, 'Bad Request');

        const result = await this.users.deleteById(userId);
        if (result.changes === 0) throw new AppError(404, 'Usuário não encontrado');

        return 'Usuário deletado com matrículas e pagamentos relacionados.';
    }
}

module.exports = UserService;
