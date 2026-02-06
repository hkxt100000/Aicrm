/**
 * 权限管理模块
 * 功能：部门管理、权限配置
 * 版本：1.1
 * 日期：2027-01-27
 */

(function() {
    'use strict';
    
    // ==================== 模块变量 ====================
    let __departmentsData = [];
    let __currentEditDepartmentId = null;

// 菜单项配置
const MENU_ITEMS = [
    { id: 'dashboard', name: '工作台', icon: 'fa-th-large' },
    { 
        id: 'customer-manage', 
        name: '客户管理', 
        icon: 'fa-users', 
        children: [
            { id: 'customers', name: '客户列表' },
            { id: 'customer-profile', name: '客户画像' },
            { id: 'enterprise-tags', name: '企业标签' },
            { id: 'enterprise-contacts', name: '企业通讯录' }
        ]
    },
    { 
        id: 'customer-groups-nav', 
        name: '客户群管理', 
        icon: 'fa-user-friends', 
        children: [
            { id: 'customer-groups', name: '客户群列表' },
            { id: 'group-tags', name: '客户群标签' }
        ]
    },
    {
        id: 'customer-ops',
        name: '客户运营',
        icon: 'fa-bullhorn',
        children: [
            { id: 'welcome-msg', name: '欢迎语设置' },
            { id: 'customer-broadcast', name: '客户群发' },
            { id: 'moments-publish', name: '发朋友圈' },
            { id: 'moments-record', name: '朋友圈记录' }
        ]
    },
    {
        id: 'group-ops',
        name: '客户群运营',
        icon: 'fa-comments',
        children: [
            { id: 'group-welcome', name: '进群欢迎语' },
            { id: 'group-broadcast', name: '客户群群发' }
        ]
    },
    {
        id: 'wecom-bot',
        name: '企微机器人',
        icon: 'fa-robot',
        children: [
            { id: 'supplier-notify', name: '供应商通知群' },
            { id: 'agent-notify', name: '代理商通知群' }
        ]
    },
    { 
        id: 'data-sources', 
        name: '源数据管理', 
        icon: 'fa-database', 
        children: [
            { id: 'data-sources-internal', name: '内部数据源' },
            { id: 'data-sources-external', name: '外部数据源' }
        ]
    },
    { 
        id: 'spreadsheet', 
        name: '企微智能表', 
        icon: 'fa-table', 
        children: [
            { id: 'spreadsheet-internal', name: '对内智能表格' },
            { id: 'spreadsheet-external', name: '对外智能表' }
        ]
    },
    {
        id: 'tianhao-data',
        name: '天号城数据',
        icon: 'fa-chart-line',
        children: [
            { id: 'order-data', name: '订单数据' },
            { id: 'supplier-data', name: '供应商数据' },
            { id: 'product-data', name: '产品数据' },
            { id: 'agent-data', name: '代理商数据' },
            { id: 'finance-data', name: '财务数据' },
            { id: 'business-data', name: '商务数据' }
        ]
    },
    { id: 'promoter', name: '推客管理', icon: 'fa-user-plus' },
    { 
        id: 'system-manage', 
        name: '系统管理', 
        icon: 'fa-cog', 
        children: [
            { id: 'settings', name: '系统配置' },
            { id: 'employee-manage', name: '员工管理' },
            { id: 'permission-manage', name: '权限管理' }
        ]
    }
];

// ==================== 初始化 ====================
let permissionManageInitialized = false;

function initPermissionManage() {
    console.log('[权限管理] 初始化权限管理模块');
    
    // 防止重复初始化
    if (permissionManageInitialized) {
        console.log('[权限管理] 已初始化，刷新数据');
        loadDepartments();
        return;
    }
    
    console.log('[权限管理] 首次初始化');
    permissionManageInitialized = true;
    
    // 绑定事件
    bindEvents();
    
    // 加载部门列表
    loadDepartments();
}

// 暴露初始化函数到全局
window.initPermissionManage = initPermissionManage;

// ==================== 事件绑定 ====================
function bindEvents() {
    // 新增部门按钮
    const addBtn = document.getElementById('addDepartmentBtn');
    if (addBtn) {
        addBtn.addEventListener('click', showAddDepartmentModal);
    }
    
    // 模态框关闭按钮
    const closeButtons = document.querySelectorAll('.modal-close, .btn-cancel');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    
    // 点击模态框背景关闭
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeAllModals();
            }
        });
    });
    
    // 保存部门按钮
    const saveBtn = document.getElementById('saveDepartmentBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', handleSaveDepartment);
    }
    
    // 确认删除按钮
    const confirmDeleteBtn = document.getElementById('confirmDeleteDepartmentBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', handleConfirmDelete);
    }
    
    // 保存权限按钮
    const savePermBtn = document.getElementById('savePermissionsBtn');
    if (savePermBtn) {
        savePermBtn.addEventListener('click', handleSavePermissions);
    }
    
    // 全选/全不选
    const selectAllBtn = document.getElementById('selectAllPermissions');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', handleSelectAllPermissions);
    }
}

// ==================== 数据加载 ====================
async function loadDepartments() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/auth/departments', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        if (result.code === 0) {
            __departmentsData = result.data || [];
            renderDepartmentList();
        } else {
            showToast(result.message || '加载部门列表失败', 'error');
        }
    } catch (error) {
        console.error('[权限管理] 加载部门失败:', error);
        showToast('加载部门列表失败，请重试', 'error');
    }
}

// ==================== 渲染函数 ====================
function renderDepartmentList() {
    const container = document.getElementById('departmentList');
    if (!container) return;
    
    if (__departmentsData.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-building"></i>
                <p>暂无部门数据</p>
                <p class="empty-hint">点击右上角"新增部门"按钮创建第一个部门</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = __departmentsData.map(dept => {
        const permCount = dept.menu_permissions ? dept.menu_permissions.length : 0;
        const empCount = dept.employee_count || 0;
        
        return `
            <div class="department-card">
                <div class="dept-header">
                    <div class="dept-info">
                        <h3 class="dept-name">
                            <i class="fas fa-building"></i>
                            ${dept.name}
                        </h3>
                        ${dept.description ? `<p class="dept-desc">${dept.description}</p>` : ''}
                    </div>
                    <div class="dept-actions">
                        <button class="btn-icon" onclick="handleConfigPermissions('${dept.id}', '${dept.name}')" title="配置权限">
                            <i class="fas fa-shield-alt"></i> 配置权限
                        </button>
                        <button class="btn-icon" onclick="handleEditDepartment('${dept.id}')" title="编辑">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-icon btn-danger" onclick="handleDeleteDepartment('${dept.id}', '${dept.name}')" title="删除">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="dept-stats">
                    <div class="stat-item">
                        <i class="fas fa-users"></i>
                        <span>员工数: <strong>${empCount}</strong></span>
                    </div>
                    <div class="stat-item">
                        <i class="fas fa-check-circle"></i>
                        <span>权限: <strong>${permCount}</strong> 个菜单</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// ==================== 模态框操作 ====================
function showAddDepartmentModal() {
    _currentEditDepartmentId = null;
    
    document.getElementById('departmentModalTitle').textContent = '新增部门';
    document.getElementById('departmentForm').reset();
    
    document.getElementById('departmentModal').style.display = 'flex';
}

async function handleEditDepartment(departmentId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/auth/departments/${departmentId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        if (result.code === 0) {
            const dept = result.data;
            __currentEditDepartmentId = departmentId;
            
            document.getElementById('departmentModalTitle').textContent = '编辑部门';
            document.getElementById('departmentName').value = dept.name;
            document.getElementById('departmentDescription').value = dept.description || '';
            
            document.getElementById('departmentModal').style.display = 'flex';
        } else {
            showToast(result.message || '获取部门信息失败', 'error');
        }
    } catch (error) {
        console.error('[权限管理] 获取部门信息失败:', error);
        showToast('获取部门信息失败，请重试', 'error');
    }
}

function closeAllModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
    __currentEditDepartmentId = null;
}

// ==================== 部门操作 ====================
async function handleSaveDepartment() {
    const name = document.getElementById('departmentName').value.trim();
    const description = document.getElementById('departmentDescription').value.trim();
    
    if (!name) {
        showToast('请输入部门名称', 'warning');
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const data = { name, description };
        
        let url = '/api/auth/departments';
        let method = 'POST';
        
        if (__currentEditDepartmentId) {
            url = `/api/auth/departments/${__currentEditDepartmentId}`;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        if (result.code === 0) {
            showToast(__currentEditDepartmentId ? '更新成功' : '创建成功', 'success');
            closeAllModals();
            loadDepartments();
        } else {
            showToast(result.message || '操作失败', 'error');
        }
    } catch (error) {
        console.error('[权限管理] 保存部门失败:', error);
        showToast('操作失败，请重试', 'error');
    }
}

function handleDeleteDepartment(departmentId, departmentName) {
    __currentEditDepartmentId = departmentId;
    document.getElementById('deleteDepartmentName').textContent = departmentName;
    document.getElementById('deleteDepartmentModal').style.display = 'flex';
}

async function handleConfirmDelete() {
    if (!__currentEditDepartmentId) return;
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/auth/departments/${__currentEditDepartmentId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        if (result.code === 0) {
            showToast('删除成功', 'success');
            closeAllModals();
            loadDepartments();
        } else {
            showToast(result.message || '删除失败', 'error');
        }
    } catch (error) {
        console.error('[权限管理] 删除部门失败:', error);
        showToast('删除失败，请重试', 'error');
    }
}

// ==================== 权限配置 ====================
async function handleConfigPermissions(departmentId, departmentName) {
    __currentEditDepartmentId = departmentId;
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/auth/departments/${departmentId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        if (result.code === 0) {
            const dept = result.data;
            const permissions = dept.menu_permissions || [];
            
            document.getElementById('permissionDepartmentName').textContent = departmentName;
            
            // 渲染权限树
            renderPermissionTree(permissions);
            
            document.getElementById('permissionModal').style.display = 'flex';
        } else {
            showToast(result.message || '获取部门信息失败', 'error');
        }
    } catch (error) {
        console.error('[权限管理] 获取部门信息失败:', error);
        showToast('获取部门信息失败，请重试', 'error');
    }
}

function renderPermissionTree(selectedPermissions) {
    const container = document.getElementById('permissionTree');
    if (!container) return;
    
    container.innerHTML = MENU_ITEMS.map(item => {
        const isChecked = selectedPermissions.includes(item.id);
        
        let html = `
            <div class="permission-item">
                <label class="permission-label">
                    <input type="checkbox" 
                           class="permission-checkbox parent-checkbox" 
                           data-id="${item.id}"
                           ${isChecked ? 'checked' : ''}
                           onchange="handlePermissionChange(this)">
                    <i class="fas ${item.icon}"></i>
                    <span>${item.name}</span>
                </label>
        `;
        
        if (item.children && item.children.length > 0) {
            html += '<div class="permission-children">';
            item.children.forEach(child => {
                const childChecked = selectedPermissions.includes(child.id);
                html += `
                    <label class="permission-label">
                        <input type="checkbox" 
                               class="permission-checkbox child-checkbox" 
                               data-id="${child.id}"
                               data-parent="${item.id}"
                               ${childChecked ? 'checked' : ''}
                               onchange="handleChildPermissionChange(this)">
                        <span>${child.name}</span>
                    </label>
                `;
            });
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    }).join('');
}

function handlePermissionChange(checkbox) {
    const parentId = checkbox.dataset.id;
    const isChecked = checkbox.checked;
    
    // 如果取消父菜单，自动取消所有子菜单
    if (!isChecked) {
        const children = document.querySelectorAll(`[data-parent="${parentId}"]`);
        children.forEach(child => {
            child.checked = false;
        });
    }
}

function handleChildPermissionChange(checkbox) {
    const parentId = checkbox.dataset.parent;
    const isChecked = checkbox.checked;
    
    // 如果选中子菜单，自动选中父菜单
    if (isChecked) {
        const parentCheckbox = document.querySelector(`[data-id="${parentId}"]`);
        if (parentCheckbox) {
            parentCheckbox.checked = true;
        }
    }
}

function handleSelectAllPermissions() {
    const checkboxes = document.querySelectorAll('.permission-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(cb => {
        cb.checked = !allChecked;
    });
}

async function handleSavePermissions() {
    if (!__currentEditDepartmentId) return;
    
    // 收集选中的权限
    const checkboxes = document.querySelectorAll('.permission-checkbox:checked');
    const permissions = Array.from(checkboxes).map(cb => cb.dataset.id);
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/auth/departments/${__currentEditDepartmentId}/permissions`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ menu_permissions: permissions })
        });
        
        const result = await response.json();
        if (result.code === 0) {
            showToast('权限配置成功', 'success');
            closeAllModals();
            loadDepartments();
        } else {
            showToast(result.message || '权限配置失败', 'error');
        }
    } catch (error) {
        console.error('[权限管理] 保存权限失败:', error);
        showToast('权限配置失败，请重试', 'error');
    }
}

// ==================== 工具函数 ====================
function showToast(message, type = 'info') {
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-times-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    }[type] || 'fas fa-info-circle';
    
    toast.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 暴露给全局供 HTML onclick 调用
window.handleEditDepartment = handleEditDepartment;
window.handleDeleteDepartment = handleDeleteDepartment;
window.handleConfigPermissions = handleConfigPermissions;
window.handlePermissionChange = handlePermissionChange;
window.handleChildPermissionChange = handleChildPermissionChange;

})(); // 立即执行函数结束
