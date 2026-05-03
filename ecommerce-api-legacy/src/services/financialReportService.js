const FinancialReportModel = require('../models/financialReportModel');

class FinancialReportService {
    constructor(db) {
        this.reports = new FinancialReportModel(db);
    }

    getFinancialReport() {
        return this.reports.listCourseRevenue();
    }
}

module.exports = FinancialReportService;
