const CheckoutService = require('../services/checkoutService');

class CheckoutController {
    constructor(db) {
        this.checkoutService = new CheckoutService(db);
    }

    checkout = async (req, res) => {
        const result = await this.checkoutService.checkout(req.body);
        return res.status(200).json(result);
    };
}

module.exports = CheckoutController;
