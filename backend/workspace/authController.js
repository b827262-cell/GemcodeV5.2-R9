const { findUserByEmail } = require('./userModel');
const { verifyPassword, generateAccessToken } = require('./security');
const rateLimit = require('express-rate-limit');

// 暴力破解保護：限制每 15 分鐘最多 5 次登入嘗試
const loginLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, 
    max: 5,
    message: { error: '太多登入嘗試，請稍後再試。' }
});

const loginHandler = async (req, res) => {
    const { email, password } = req.body;

    // 1. 查找用戶
    const user = findUserByEmail(email);
    
    // 2. 驗證 (統一返回錯誤避免枚舉攻擊)
    if (!user || !(await verifyPassword(user.passwordHash, password))) {
        return res.status(401).json({ error: '帳號或密碼錯誤' });
    }

    // 3. 簽發 Token
    const token = generateAccessToken(user);
    res.json({ token });
};

module.exports = { loginHandler, loginLimiter };
