const UserService = require('../services/userService');

class UserController {
    constructor(db) {
        this.userService = new UserService(db);
    }

    delete = async (req, res) => {
        const message = await this.userService.deleteUser(req.params.id);
        return res.send(message);
    };
}

module.exports = UserController;
