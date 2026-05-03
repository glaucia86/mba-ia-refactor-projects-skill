const cache = new Map();

function save(key, value) {
    cache.set(key, value);
}

module.exports = { save };
