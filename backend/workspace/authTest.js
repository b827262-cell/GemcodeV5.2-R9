const { createUser, findUserByEmail } = require('./userModel');
const { hashPassword, verifyPassword } = require('./security');

async function runTests() {
    console.log("--- 啟動驗證測試 ---");

    // 1. 測試：註冊與加密
    const password = "mySecretPassword";
    const hash = await hashPassword(password);
    createUser("test@example.com", hash);
    console.log("✅ 用戶註冊與密碼加密測試通過");

    // 2. 測試：登入流程 (正確密碼)
    const user = findUserByEmail("test@example.com");
    const isMatch = await verifyPassword(user.passwordHash, password);
    if (!isMatch) throw new Error("密碼驗證失敗");
    console.log("✅ 密碼正確登入驗證通過");

    // 3. 測試：錯誤密碼 (安全性防護)
    const isWrongMatch = await verifyPassword(user.passwordHash, "wrongPassword");
    if (isWrongMatch) throw new Error("密碼錯誤竟然通過了驗證");
    console.log("✅ 錯誤密碼拒絕測試通過");

    console.log("--- 所有核心邏輯測試完成 ---");
}

runTests().catch(err => console.error("測試失敗:", err));
