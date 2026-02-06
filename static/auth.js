/**
 * 认证模块
 * 处理登录、登出、token 管理、权限检查
 */

// API 基础路径
const AUTH_API_BASE = '/api/auth';

// 认证管理器
const authManager = {
    /**
     * 获取存储的 token
     */
    getToken() {
        return localStorage.getItem('token');
    },

    /**
     * 保存 token
     */
    setToken(token) {
        localStorage.setItem('token', token);
    },

    /**
     * 获取用户信息
     */
    getUserInfo() {
        const userInfoStr = localStorage.getItem('userInfo');
        if (!userInfoStr) return null;
        
        try {
            return JSON.parse(userInfoStr);
        } catch {
            return null;
        }
    },

    /**
     * 保存用户信息
     */
    setUserInfo(userInfo) {
        localStorage.setItem('userInfo', JSON.stringify(userInfo));
    },

    /**
     * 清除认证信息
     */
    clearAuth() {
        localStorage.removeItem('token');
        localStorage.removeItem('userInfo');
    },

    /**
     * 检查是否已登录
     */
    isLoggedIn() {
        return !!this.getToken();
    },

    /**
     * 检查是否为超级管理员
     */
    isSuperAdmin() {
        const userInfo = this.getUserInfo();
        return userInfo && userInfo.is_super_admin === true;
    },

    /**
     * 检查菜单权限
     */
    hasMenuPermission(menuId) {
        const userInfo = this.getUserInfo();
        if (!userInfo) return false;

        // 超级管理员拥有所有权限
        if (userInfo.is_super_admin) return true;

        // 检查菜单权限
        const permissions = userInfo.menu_permissions || [];
        return permissions.includes(menuId);
    },

    /**
     * 获取当前用户信息（从服务器）
     */
    async fetchCurrentUser() {
        const token = this.getToken();
        if (!token) {
            return null;
        }

        try {
            const response = await fetch(`${AUTH_API_BASE}/current`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await response.json();

            if (data.code === 0) {
                // 更新本地存储
                this.setUserInfo(data.data);
                return data.data;
            } else {
                // Token 无效，清除
                this.clearAuth();
                return null;
            }
        } catch (error) {
            console.error('[Auth] 获取用户信息失败:', error);
            return null;
        }
    },

    /**
     * 登出
     */
    async logout() {
        const token = this.getToken();
        
        if (token) {
            try {
                await fetch(`${AUTH_API_BASE}/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            } catch (error) {
                console.error('登出请求失败:', error);
            }
        }

        // 清除本地存储
        this.clearAuth();

        // 跳转到登录页
        window.location.href = '/static/login.html';
    },

    /**
     * 初始化认证检查
     * 在页面加载时调用
     */
    async initAuthCheck() {
        // 如果当前在登录页，不需要检查
        if (window.location.pathname.includes('login.html')) {
            return;
        }

        const token = this.getToken();
        
        // 没有 token，跳转到登录页
        if (!token) {
            window.location.href = '/static/login.html';
            return;
        }

        // 验证 token 有效性
        const user = await this.fetchCurrentUser();
        
        if (!user) {
            // Token 无效，跳转到登录页
            window.location.href = '/static/login.html';
            return;
        }

        // Token 有效，初始化页面
        this.initUserInterface(user);
        
        return user;
    },

    /**
     * 初始化用户界面
     */
    initUserInterface(user) {
        // 显示用户信息
        this.displayUserInfo(user);

        // 根据权限显示/隐藏菜单
        this.applyMenuPermissions(user);

        // 添加登出按钮事件
        this.attachLogoutHandler();
    },

    /**
     * 显示用户信息
     */
    displayUserInfo(user) {
        // 在顶部显示用户信息
        const headerRight = document.querySelector('.header-right');
        if (!headerRight) return;

        // 构建用户信息 HTML
        let userInfoHTML = `
            <div class="user-info">
                <span class="user-name">${user.name || user.account}</span>
        `;

        // 如果绑定了企业微信，显示企业微信名称
        if (user.wecom_name) {
            userInfoHTML += `
                <span class="user-wecom">（企微: ${user.wecom_name}）</span>
            `;
        }

        // 超级管理员标识
        if (user.is_super_admin) {
            userInfoHTML += `
                <span class="user-badge">超管</span>
            `;
        }

        userInfoHTML += `
                <button class="logout-btn" onclick="authManager.logout()">
                    退出登录
                </button>
            </div>
        `;

        headerRight.innerHTML = userInfoHTML;
    },

    /**
     * 根据权限应用菜单显示
     */
    applyMenuPermissions(user) {
        // 超级管理员看到所有菜单
        if (user.is_super_admin) {
            return;
        }

        const permissions = user.menu_permissions || [];
        
        // 隐藏所有导航组和导航项
        document.querySelectorAll('.nav-group, .nav-item').forEach(item => {
            // 跳过子项（它们由父项控制）
            if (item.classList.contains('nav-sub-item')) {
                return;
            }
            
            // 跳过导航组切换按钮
            if (item.classList.contains('nav-group-toggle')) {
                return;
            }
            
            const module = item.dataset.module;
            
            if (!module) {
                // 对于导航组，检查是否有子项有权限
                if (item.classList.contains('nav-group')) {
                    const subItems = item.querySelectorAll('.nav-sub-item[data-module]');
                    let hasPermission = false;
                    
                    subItems.forEach(subItem => {
                        const subModule = subItem.dataset.module;
                        if (permissions.includes(subModule)) {
                            hasPermission = true;
                            subItem.style.display = '';
                        } else {
                            subItem.style.display = 'none';
                        }
                    });
                    
                    // 如果有子项有权限，显示导航组，否则隐藏
                    if (hasPermission) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                }
                return;
            }
            
            // 检查单个导航项的权限
            if (permissions.includes(module)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    },

    /**
     * 附加登出按钮事件
     */
    attachLogoutHandler() {
        // 已在 displayUserInfo 中通过 onclick 处理
    }
};

// 封装 fetch 请求，自动添加 Authorization header
async function authFetch(url, options = {}) {
    const token = authManager.getToken();
    
    if (!token) {
        // 没有 token，跳转到登录页
        window.location.href = '/static/login.html';
        return;
    }

    // 合并 headers
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        // 检查是否 401 未授权
        if (response.status === 401) {
            // Token 失效，清除并跳转
            authManager.clearAuth();
            window.location.href = '/static/login.html';
            return;
        }

        return response;
    } catch (error) {
        console.error('请求失败:', error);
        throw error;
    }
}

// 页面加载时初始化认证检查
document.addEventListener('DOMContentLoaded', async function() {
    // 只在非登录页执行检查
    if (!window.location.pathname.includes('login.html')) {
        await authManager.initAuthCheck();
    }
});
