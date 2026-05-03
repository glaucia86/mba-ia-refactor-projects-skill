const PaymentStatus = {
    PAID: 'PAID',
    DENIED: 'DENIED'
};

function processPayment(cardNumber) {
    return String(cardNumber).startsWith('4') ? PaymentStatus.PAID : PaymentStatus.DENIED;
}

module.exports = { PaymentStatus, processPayment };
