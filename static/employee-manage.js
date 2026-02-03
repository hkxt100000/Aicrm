/**
 * 员工管理模块
 * 功能：员工列表、新增、编辑、删除、启用/禁用、重置密码
 * 版本：1.1
 * 日期：2027-01-27
 */

(function() {
    'use strict';
    
    // ==================== 模块变量 ====================
    let __employeesData = [];
    let __departmentsData = [];
    let __currentPage = 1;
    const __pageSize = 20;
    let __totalCount = 0;
    let __currentEditEmployeeId = null;

    
    // ==================== 初始化 ====================
    let employeeManageInitialized = false;
    
    function initEmployeeManage() {
    console.log('[员工管理] 初始化员工管理模块');
    
    // 防止重复初始化
    if (employeeManageInitialized) {
        console.log('[员工管理] 已初始化，刷新数据');
        loadEmployees();
        return;
    }
    
    console.log('[员工管理] 首次初始化');
    employeeManageInitialized = true;
    
    // 绑定事件
    bindEvents();
    
    // 加载部门列表
    loadDepartments();
    
    // 加载员工列表
    loadEmployees();
    }
    
    // 暴露初始化函数到全局
    window.initEmployeeManage = initEmployeeManage;
    
    // ==================== 事件绑定 ====================
    function bindEvents() {
    // 新增员工按钮
    const addBtn = document.getElementById('addEmployeeBtn');
    if (addBtn) {
        addBtn.addEventListener('click', showAddEmployeeModal);
    }
    
    // 搜索按钮
    const searchBtn = document.getElementById('searchEmployeeBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', handleSearch);
    }
    
    // 搜索输入框回车
    const searchInput = document.getElementById('employeeSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
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
    
    // 保存员工按钮
    const saveBtn = document.getElementById('saveEmployeeBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', handleSaveEmployee);
    }
    
    // 确认删除按钮
    const confirmDeleteBtn = document.getElementById('confirmDeleteEmployeeBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', handleConfirmDelete);
    }
    
    // 确认重置密码按钮
    const confirmResetBtn = document.getElementById('confirmResetPasswordBtn');
    if (confirmResetBtn) {
        confirmResetBtn.addEventListener('click', handleConfirmResetPassword);
    }
}

// ==================== 数据加载 ====================
// 加载部门列表
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
            updateDepartmentSelect();
        }
    } catch (error) {
        console.error('[员工管理] 加载部门失败:', error);
    }
}

// 更新部门下拉框
function updateDepartmentSelect() {
    const select = document.getElementById('employeeDepartment');
    if (!select) return;
    
    select.innerHTML = '<option value="">未分配部门</option>';
    __departmentsData.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        select.appendChild(option);
    });
}

// 加载员工列表
async function loadEmployees(page = 1, search = '') {
    try {
        const token = localStorage.getItem('token');
        const params = new URLSearchParams({
            page: page,
            limit: __pageSize
        });
        
        if (search) {
            params.append('search', search);
        }
        
        const response = await fetch(`/api/auth/employees?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        if (result.code === 0) {
            __employeesData = result.data || [];
            __totalCount = result.total || 0;
            __currentPage = page;
            
            renderEmployeeTable();
            renderPagination();
        } else {
            showToast(result.message || '加载员工列表失败', 'error');
        }
    } catch (error) {
        console.error('[员工管理] 加载员工列表失败:', error);
        showToast('加载员工列表失败，请重试', 'error');
    }
}

// ==================== 渲染函数 ====================
// 渲染员工表格
function renderEmployeeTable() {
    const tbody = document.querySelector('#employeeTable tbody');
    if (!tbody) return;
    
    if (__employeesData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 40px; color: #999;">
                    暂无员工数据
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = __employeesData.map(emp => {
        const statusClass = emp.status === 'active' ? 'status-active' : 'status-inactive';
        const statusText = emp.status === 'active' ? '正常' : '已禁用';
        const department = __departmentsData.find(d => d.id === emp.department_id);
        const departmentName = department ? department.name : '-';
        const isSuperAdmin = emp.is_super_admin ? '<span class="badge-super-admin">超管</span>' : '';
        const wecomInfo = emp.wecom_name ? `<div class="wecom-info">${emp.wecom_name}</div>` : '';
        
        // 超级管理员不能删除和禁用
        const canDelete = !emp.is_super_admin;
        const canDisable = !emp.is_super_admin;
        
        return `
            <tr>
                <td>${emp.account}</td>
                <td>
                    ${emp.name} ${isSuperAdmin}
                    ${wecomInfo}
                </td>
                <td>${departmentName}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>${formatDate(emp.created_at)}</td>
                <td>${formatDate(emp.updated_at)}</td>
                <td class="table-actions">
                    <button class="btn-icon" onclick="handleEditEmployee('${emp.id}')" title="编辑">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" onclick="handleResetPassword('${emp.id}', '${emp.name}')" title="重置密码">
                        <i class="fas fa-key"></i>
                    </button>
                    ${canDisable ? `
                        <button class="btn-icon" onclick="handleToggleStatus('${emp.id}', '${emp.status}')" title="${emp.status === 'active' ? '禁用' : '启用'}">
                            <i class="fas fa-${emp.status === 'active' ? 'ban' : 'check'}"></i>
                        </button>
                    ` : ''}
                    ${canDelete ? `
                        <button class="btn-icon btn-danger" onclick="handleDeleteEmployee('${emp.id}', '${emp.name}')" title="删除">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                </td>
            </tr>
        `;
    }).join('');
}

// 渲染分页
function renderPagination() {
    const container = document.getElementById('employeePagination');
    if (!container) return;
    
    const totalPages = Math.ceil(__totalCount / __pageSize);
    
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<div class="pagination">';
    
    // 上一页
    if (__currentPage > 1) {
        html += `<button class="page-btn" onclick="loadEmployees(${__currentPage - 1})">上一页</button>`;
    }
    
    // 页码
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= __currentPage - 2 && i <= __currentPage + 2)) {
            html += `<button class="page-btn ${i === __currentPage ? 'active' : ''}" onclick="loadEmployees(${i})">${i}</button>`;
        } else if (i === __currentPage - 3 || i === __currentPage + 3) {
            html += `<span class="page-ellipsis">...</span>`;
        }
    }
    
    // 下一页
    if (__currentPage < totalPages) {
        html += `<button class="page-btn" onclick="loadEmployees(${__currentPage + 1})">下一页</button>`;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

// ==================== 模态框操作 ====================
// 显示新增员工模态框
function showAddEmployeeModal() {
    __currentEditEmployeeId = null;
    
    document.getElementById('modalTitle').textContent = '新增员工';
    document.getElementById('employeeForm').reset();
    
    // 显示密码字段
    document.getElementById('passwordField').style.display = 'block';
    
    document.getElementById('employeeModal').style.display = 'flex';
}

// 显示编辑员工模态框
async function handleEditEmployee(employeeId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/auth/employees/${employeeId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        if (result.code === 0) {
            const employee = result.data;
            __currentEditEmployeeId = employeeId;
            
            document.getElementById('modalTitle').textContent = '编辑员工';
            document.getElementById('employeeAccount').value = employee.account;
            document.getElementById('employeeName').value = employee.name;
            document.getElementById('employeeDepartment').value = employee.department_id || '';
            document.getElementById('employeeWecomUserId').value = employee.wecom_user_id || '';
            document.getElementById('employeeWecomName').value = employee.wecom_name || '';
            
            // 隐藏密码字段
            document.getElementById('passwordField').style.display = 'none';
            
            document.getElementById('employeeModal').style.display = 'flex';
        } else {
            showToast(result.message || '获取员工信息失败', 'error');
        }
    } catch (error) {
        console.error('[员工管理] 获取员工信息失败:', error);
        showToast('获取员工信息失败，请重试', 'error');
    }
}

// 关闭所有模态框
function closeAllModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
    __currentEditEmployeeId = null;
}

// ==================== 员工操作 ====================
// 保存员工
async function handleSaveEmployee() {
    const account = document.getElementById('employeeAccount').value.trim();
    const name = document.getElementById('employeeName').value.trim();
    const password = document.getElementById('employeePassword').value.trim();
    const departmentId = document.getElementById('employeeDepartment').value;
    const wecomUserId = document.getElementById('employeeWecomUserId').value.trim();
    const wecomName = document.getElementById('employeeWecomName').value.trim();
    
    // 验证
    if (!account) {
        showToast('请输入登录账号', 'warning');
        return;
    }
    
    if (!name) {
        showToast('请输入员工姓名', 'warning');
        return;
    }
    
    // 新增时必须填写密码
    if (!__currentEditEmployeeId && !password) {
        showToast('请输入登录密码', 'warning');
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const data = {
            account,
            name,
            department_id: departmentId || null,
            wecom_user_id: wecomUserId || null,
            wecom_name: wecomName || null
        };
        
        let url = '/api/auth/employees';
        let method = 'POST';
        
        if (__currentEditEmployeeId) {
            // 编辑
            url = `/api/auth/employees/${__currentEditEmployeeId}`;
            method = 'PUT';
        } else {
            // 新增
            data.password = password;
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
            showToast(__currentEditEmployeeId ? '更新成功' : '创建成功', 'success');
            closeAllModals();
            loadEmployees(__currentPage);
        } else {
            showToast(result.message || '操作失败', 'error');
        }
    } catch (error) {
        console.error('[员工管理] 保存员工失败:', error);
        showToast('操作失败，请重试', 'error');
    }
}

// 删除员工
function handleDeleteEmployee(employeeId, employeeName) {
    __currentEditEmployeeId = employeeId;
    document.getElementById('deleteEmployeeName').textContent = employeeName;
    document.getElementById('deleteModal').style.display = 'flex';
}

// 确认删除
async function handleConfirmDelete() {
    if (!__currentEditEmployeeId) return;
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/auth/employees/${__currentEditEmployeeId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        if (result.code === 0) {
            showToast('删除成功', 'success');
            closeAllModals();
            loadEmployees(__currentPage);
        } else {
            showToast(result.message || '删除失败', 'error');
        }
    } catch (error) {
        console.error('[员工管理] 删除员工失败:', error);
        showToast('删除失败，请重试', 'error');
    }
}

// 切换员工状态
async function handleToggleStatus(employeeId, currentStatus) {
    const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
    const action = newStatus === 'active' ? '启用' : '禁用';
    
    if (!confirm(`确定要${action}该员工吗？`)) {
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/auth/employees/${employeeId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        const result = await response.json();
        if (result.code === 0) {
            showToast(`${action}成功`, 'success');
            loadEmployees(__currentPage);
        } else {
            showToast(result.message || `${action}失败`, 'error');
        }
    } catch (error) {
        console.error('[员工管理] 切换员工状态失败:', error);
        showToast(`${action}失败，请重试`, 'error');
    }
}

// 重置密码
function handleResetPassword(employeeId, employeeName) {
    __currentEditEmployeeId = employeeId;
    document.getElementById('resetPasswordEmployeeName').textContent = employeeName;
    document.getElementById('resetPasswordModal').style.display = 'flex';
}

// 确认重置密码
async function handleConfirmResetPassword() {
    if (!__currentEditEmployeeId) return;
    
    const newPassword = document.getElementById('newPassword').value.trim();
    
    if (!newPassword) {
        showToast('请输入新密码', 'warning');
        return;
    }
    
    if (newPassword.length < 6) {
        showToast('密码长度不能少于6位', 'warning');
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/auth/employees/${__currentEditEmployeeId}/reset-password`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ new_password: newPassword })
        });
        
        const result = await response.json();
        if (result.code === 0) {
            showToast('重置密码成功', 'success');
            closeAllModals();
            document.getElementById('newPassword').value = '';
        } else {
            showToast(result.message || '重置密码失败', 'error');
        }
    } catch (error) {
        console.error('[员工管理] 重置密码失败:', error);
        showToast('重置密码失败，请重试', 'error');
    }
}

// ==================== 搜索 ====================
function handleSearch() {
    const searchInput = document.getElementById('employeeSearchInput');
    const searchText = searchInput ? searchInput.value.trim() : '';
    loadEmployees(1, searchText);
}

// ==================== 工具函数 ====================
// 格式化日期
function formatDate(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

// 显示提示消息
function showToast(message, type = 'info') {
    // 移除已存在的 toast
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
    
    // 显示动画
    setTimeout(() => toast.classList.add('show'), 10);
    
    // 3秒后自动消失
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
    }
    
    // 暴露给全局供 HTML onclick 调用
    window.handleEditEmployee = handleEditEmployee;
    window.handleDeleteEmployee = handleDeleteEmployee;
    window.handleToggleStatus = handleToggleStatus;
    window.handleResetPassword = handleResetPassword;

})(); // 立即执行函数结束
