const AppError = require('../errors/AppError');

function errorHandler(err, req, res, next) {
    if (err instanceof AppError) {
        return res.status(err.statusCode).send(err.message);
    }

    console.error('Erro inesperado na requisicao', err);
    return res.status(500).send('Erro interno');
}

module.exports = { errorHandler };
