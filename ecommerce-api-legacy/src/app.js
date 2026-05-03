const express = require('express');
const settings = require('./config/settings');
const { createDatabase, initializeDatabase } = require('./database/connection');
const checkoutRoutes = require('./routes/checkoutRoutes');
const adminRoutes = require('./routes/adminRoutes');
const userRoutes = require('./routes/userRoutes');
const { errorHandler } = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

async function start() {
    const db = createDatabase();
    await initializeDatabase(db);

    app.use(checkoutRoutes(db));
    app.use(adminRoutes(db));
    app.use(userRoutes(db));
    app.use(errorHandler);

    app.listen(settings.port, () => {
        console.log(`LMS API rodando na porta ${settings.port}...`);
    });
}

start().catch((err) => {
    console.error('Falha ao iniciar a aplicacao', err);
    process.exit(1);
});
