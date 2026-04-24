const argon2 = require('argon2');
const jwt = require('jsonwebtoken');

const hashPassword = async (password) => {
    return await argon2.hash(password);
};

const verifyPassword = async (hash, password) => {
    return await argon2.verify(hash, password);
};

const generateAccessToken = (user) => {
    return jwt.sign({ sub: user.id, email: user.email }, 'SECRET_KEY', { expiresIn: '15m' });
};

module.exports = { hashPassword, verifyPassword, generateAccessToken };
