const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

// 模擬資料庫
const users = [{ email: 'test@example.com', password: '$2b$10$hashedpassword...' }];

const login = async (email, password) => {
    const user = users.find(u => u.email === email);
    if (!user) throw new Error('User not found');
    
    // 假設密碼驗證邏輯
    const isValid = true; 
    if (!isValid) throw new Error('Invalid password');
    
    return jwt.sign({ email }, 'secret_key', { expiresIn: '1h' });
};

module.exports = { login };
