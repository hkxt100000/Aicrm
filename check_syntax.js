const fs = require('fs');

console.log('=== JavaScript 语法检查工具 ===\n');

const filePath = 'static/script.js';

if (!fs.existsSync(filePath)) {
    console.error(`❌ 文件不存在: ${filePath}`);
    process.exit(1);
}

console.log(`📝 检查文件: ${filePath}\n`);

try {
    const content = fs.readFileSync(filePath, 'utf-8');
    
    // 尝试用 Function 构造函数检查语法
    new Function(content);
    
    console.log('✅ 语法检查通过！');
    console.log(`\n文件大小: ${(content.length / 1024).toFixed(2)} KB`);
    console.log(`行数: ${content.split('\n').length}`);
    
    // 检查函数定义
    const functions = content.match(/function\s+\w+\s*\(/g);
    console.log(`\n函数数量: ${functions ? functions.length : 0}`);
    
    // 检查特定函数
    if (content.includes('function showUploadExcelDialog')) {
        console.log('✅ 找到 showUploadExcelDialog 函数');
    } else {
        console.log('❌ 未找到 showUploadExcelDialog 函数');
    }
    
    if (content.includes('function closeUploadExcelDialog')) {
        console.log('✅ 找到 closeUploadExcelDialog 函数');
    } else {
        console.log('❌ 未找到 closeUploadExcelDialog 函数');
    }
    
} catch (error) {
    console.error('❌ 语法错误:');
    console.error(error.message);
    
    if (error.stack) {
        console.error('\n错误堆栈:');
        console.error(error.stack);
    }
    
    process.exit(1);
}
