const FinancialReportService = require('../services/financialReportService');

class AdminController {
    constructor(db) {
        this.financialReportService = new FinancialReportService(db);
    }

    financialReport = async (req, res) => {
        const report = await this.financialReportService.getFinancialReport();
        return res.json(report);
    };
}

module.exports = AdminController;
