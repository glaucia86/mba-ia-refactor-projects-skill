const settings = {
    port: Number(process.env.PORT || 3000),
    database: {
        filename: process.env.SQLITE_FILENAME || ':memory:'
    },
    payment: {
        gatewayKey: process.env.PAYMENT_GATEWAY_KEY || ''
    },
    adminToken: process.env.ADMIN_TOKEN || ''
};

module.exports = settings;
