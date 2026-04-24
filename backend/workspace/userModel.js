const crypto = require('crypto');

const users = new Map();

const createUser = (email, passwordHash) => {
    const user = {
        id: crypto.randomUUID(),
        email,
        passwordHash,
        createdAt: new Date()
    };
    users.set(email, user);
    return user;
};

const findUserByEmail = (email) => users.get(email);

module.exports = { createUser, findUserByEmail };
