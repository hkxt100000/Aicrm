/**
 * 前端调试脚本
 * 在浏览器控制台运行，检查 Token 和请求
 */

console.log('=== 前端调试 ===');

// 1. 检查 localStorage
console.log('\n1. 检查 localStorage:');
const token = localStorage.getItem('token');
const userInfo = localStorage.getItem('userInfo');

console.log('Token:', token ? `${token.substring(0, 20)}... (长度: ${token.length})` : '❌ 不存在');
console.log('UserInfo:', userInfo ? JSON.parse(userInfo) : '❌ 不存在');

// 2. 测试 Token
if (token) {
    console.log('\n2. 测试 /api/auth/current:');
    fetch('/api/auth/current', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(res => {
        console.log('Status:', res.status);
        return res.json();
    })
    .then(data => {
        console.log('Response:', data);
    })
    .catch(err => {
        console.error('❌ 错误:', err);
    });
    
    console.log('\n3. 测试 /api/auth/employees:');
    fetch('/api/auth/employees?page=1&limit=10', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(res => {
        console.log('Status:', res.status);
        return res.json();
    })
    .then(data => {
        console.log('Response:', data);
        if (data.code === 0) {
            console.log('✅ 成功! 员工数量:', data.data?.total);
        } else {
            console.log('❌ 失败:', data.message);
        }
    })
    .catch(err => {
        console.error('❌ 错误:', err);
    });
} else {
    console.log('\n❌ Token 不存在，请先登录！');
}

console.log('\n=== 调试完成 ===');
console.log('请查看上面的输出，特别注意：');
console.log('1. Token 是否存在？');
console.log('2. /api/auth/current 返回什么？');
console.log('3. /api/auth/employees 返回什么？');
