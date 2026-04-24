document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;

    // 極簡驗證邏輯
    if (user === 'admin' && pass === '1234') {
        alert('登入成功！');
    } else {
        alert('帳號或密碼錯誤。');
    }
});