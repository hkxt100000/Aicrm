/**
 * Apple 风格对话框 JavaScript
 * 版本：1.0
 * 日期：2026-01-27
 */

// Apple Alert 提示框
window.appleAlert = function(message, title = '提示') {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'apple-alert-overlay';
        
        const alert = document.createElement('div');
        alert.className = 'apple-alert';
        
        alert.innerHTML = `
            <div class="apple-alert-title">${title}</div>
            <div class="apple-alert-message">${message}</div>
            <button class="apple-alert-button">确定</button>
        `;
        
        overlay.appendChild(alert);
        document.body.appendChild(overlay);
        
        const button = alert.querySelector('.apple-alert-button');
        button.onclick = () => {
            overlay.remove();
            resolve();
        };
        
        // 点击遮罩关闭
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                overlay.remove();
                resolve();
            }
        };
        
        // ESC键关闭
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                overlay.remove();
                resolve();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
    });
};

// Apple Confirm 确认框
window.appleConfirm = function(message, title = '确认', options = {}) {
    return new Promise((resolve) => {
        const {
            confirmText = '确定',
            cancelText = '取消',
            isDanger = false
        } = options;
        
        const overlay = document.createElement('div');
        overlay.className = 'apple-alert-overlay';
        
        const confirm = document.createElement('div');
        confirm.className = 'apple-confirm';
        
        confirm.innerHTML = `
            <div class="apple-confirm-title">${title}</div>
            <div class="apple-confirm-message">${message}</div>
            <div class="apple-confirm-buttons">
                <button class="apple-confirm-button apple-confirm-button-cancel">${cancelText}</button>
                <button class="apple-confirm-button ${isDanger ? 'apple-confirm-button-danger' : 'apple-confirm-button-confirm'}">${confirmText}</button>
            </div>
        `;
        
        overlay.appendChild(confirm);
        document.body.appendChild(overlay);
        
        const buttons = confirm.querySelectorAll('.apple-confirm-button');
        buttons[0].onclick = () => {
            overlay.remove();
            resolve(false);
        };
        buttons[1].onclick = () => {
            overlay.remove();
            resolve(true);
        };
        
        // 点击遮罩关闭
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                overlay.remove();
                resolve(false);
            }
        };
        
        // ESC键取消
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                overlay.remove();
                resolve(false);
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
    });
};

// Apple Toast 提示
window.appleToast = function(message, type = 'default', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `apple-toast${type !== 'default' ? ' apple-toast-' + type : ''}`;
    
    let icon = '';
    if (type === 'success') icon = '<i class="fas fa-check-circle apple-toast-icon"></i>';
    else if (type === 'error') icon = '<i class="fas fa-times-circle apple-toast-icon"></i>';
    else if (type === 'warning') icon = '<i class="fas fa-exclamation-circle apple-toast-icon"></i>';
    
    toast.innerHTML = `${icon}<span>${message}</span>`;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('fadeOut');
        setTimeout(() => toast.remove(), 300);
    }, duration);
};

// 替换原生 alert
if (typeof window.originalAlert === 'undefined') {
    window.originalAlert = window.alert;
    window.alert = function(message) {
        appleAlert(message);
    };
}

// 替换原生 confirm
if (typeof window.originalConfirm === 'undefined') {
    window.originalConfirm = window.confirm;
    window.confirm = function(message) {
        return new Promise((resolve) => {
            appleConfirm(message).then(resolve);
        });
    };
}

// 导出函数
window.showSuccess = function(message) {
    appleToast(message, 'success');
};

window.showError = function(message) {
    appleToast(message, 'error');
};

window.showWarning = function(message) {
    appleToast(message, 'warning');
};

window.showInfo = function(message) {
    appleToast(message);
};

console.log('[Apple Dialogs] 已加载 Apple 风格对话框');
