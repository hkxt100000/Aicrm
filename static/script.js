// ========== 全局变量 ==========
let currentPage = 1;
let totalPages = 1;
let totalCount = 0;
let pageLimit = 20;
let selectedCustomers = [];
let apiToken = localStorage.getItem('api_token') || 'crm-default-token';
let selectedTags = [];
let selectedProvinces = [];
let allTagGroups = [];

// ========== 页面加载 ==========
document.addEventListener('DOMContentLoaded', () => {
    console.log('[初始化] 页面加载完成');
    
    // 加载配置
    loadConfig();
    
    // 加载员工列表（用于筛选下拉框）
    loadEmployees();
    
    // 加载标签列表（用于筛选下拉框）
    loadTags();
    
    // 默认显示工作台
    switchModule('dashboard');
    
    // 导航切换
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const module = item.dataset.module;
            switchModule(module);
        });
    });
    
    // 使用事件委托绑定"上传 Excel"按钮（重要！）
    // 这样即使按钮在模块切换时被重新渲染，事件也能正常工作
    document.body.addEventListener('click', (e) => {
        // 检查点击的元素或其父元素是否是上传按钮
        const btn = e.target.closest('#btn-upload-excel');
        if (btn) {
            console.log('[事件] 上传按钮被点击（通过事件委托）');
            e.preventDefault();
            e.stopPropagation();
            showUploadExcelDialog();
        }
        
        // 检查是否是手工创建表格按钮
        const createBtn = e.target.closest('#btn-create-table');
        if (createBtn) {
            console.log('[事件] 手工创建表格按钮被点击');
            e.preventDefault();
            e.stopPropagation();
            showCreateTableDialog();
        }
    });
    
    console.log('[初始化] 事件委托已设置');
});

// ========== 模块切换 ==========
function switchModule(moduleName) {
    console.log('[切换模块]', moduleName);
    
    // 更新导航状态 - 排除nav-group-toggle
    document.querySelectorAll('.nav-item:not(.nav-group-toggle)').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.module === moduleName) {
            item.classList.add('active');
        }
    });
    
    // 更新内容显示
    document.querySelectorAll('.module').forEach(module => {
        module.classList.remove('active');
    });
    
    const targetModule = document.getElementById(`module-${moduleName}`);
    console.log('[目标模块]', `module-${moduleName}`, targetModule);
    
    if (targetModule) {
        targetModule.classList.add('active');
    } else {
        console.error('[模块不存在]', `module-${moduleName}`);
    }
    
    // 更新面包屑
    const breadcrumbMap = {
        'dashboard': '工作台',
        'customers': '客户管理',
        'customer-profile': '客户画像',
        'customer-tags': '客户标签',
        'customer-groups': '客户群列表',
        'group-tags': '客户群标签',
        'contacts': '通讯录',
        'enterprise-contacts': '企业通讯录',
        'enterprise-tags': '企业标签',
        'spreadsheet': '智能表格',
        'data': '数据分析',
        'operations': '运营工具',
        'settings': '系统设置'
    };
    const breadcrumbCurrent = document.getElementById('breadcrumb-current');
    if (breadcrumbCurrent) {
        breadcrumbCurrent.textContent = breadcrumbMap[moduleName] || '未知模块';
    }
    
    // 根据模块加载数据
    console.log('[准备加载数据]', moduleName);
    if (moduleName === 'dashboard') {
        // 工作台数据加载（如果需要）
    } else if (moduleName === 'customers') {
        loadCustomers();
    } else if (moduleName === 'spreadsheet') {
        loadSpreadsheetList();
    } else if (moduleName === 'contacts' || moduleName === 'enterprise-contacts') {
        console.log('[加载员工列表]');
        loadEmployeesList();
    } else if (moduleName === 'enterprise-tags') {
        console.log('[加载企业标签]');
        loadEnterpriseTagsList();
    } else if (moduleName === 'customer-groups') {
        console.log('[加载客户群列表]');
        loadCustomerGroups();
        loadTagsToFilter(); // 加载标签到筛选器
    } else if (moduleName === 'group-tags') {
        console.log('[加载客户群标签]');
        // 延迟执行，确保 group-tags.js 已加载
        setTimeout(() => {
            if (typeof window.loadGroupTags === 'function') {
                window.loadGroupTags();
            } else {
                console.error('[错误] loadGroupTags 函数未找到');
            }
        }, 100);
    } else if (moduleName === 'settings') {
        console.log('[加载系统设置]');
        loadWecomConfig();
    }
}

// ========== Toast 提示 ==========
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ========== 配置管理 ==========
function showConfig() {
    const config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
    
    document.getElementById('config-corpid').value = config.corpid || '';
    document.getElementById('config-contact-secret').value = config.contact_secret || '';
    document.getElementById('config-app-secret').value = config.app_secret || '';
    document.getElementById('config-customer-secret').value = config.customer_secret || '';
    document.getElementById('config-agentid').value = config.agentid || '';
    document.getElementById('config-api-token').value = apiToken;
    
    document.getElementById('config-modal').classList.add('show');
}

function closeConfig() {
    document.getElementById('config-modal').classList.remove('show');
}

function saveConfig() {
    const config = {
        corpid: document.getElementById('config-corpid').value,
        contact_secret: document.getElementById('config-contact-secret').value,
        app_secret: document.getElementById('config-app-secret').value,
        customer_secret: document.getElementById('config-customer-secret').value,
        agentid: document.getElementById('config-agentid').value
    };
    
    const token = document.getElementById('config-api-token').value;
    
    // 企业 ID 必填，至少要有一个 Secret
    if (!config.corpid) {
        showToast('请填写企业 ID', 'error');
        return;
    }
    
    if (!config.contact_secret && !config.app_secret && !config.customer_secret) {
        showToast('请至少填写一个 Secret（推荐填写自建应用 Secret）', 'error');
        return;
    }
    
    localStorage.setItem('wecom_config', JSON.stringify(config));
    localStorage.setItem('api_token', token);
    apiToken = token;
    
    showToast('配置保存成功！', 'success');
    closeConfig();
}

function loadConfig() {
    const config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
    console.log('[配置] 已加载配置', config);
}

// ========== 同步数据 ==========
async function syncData() {
    showToast('正在同步数据，请稍候...', 'info');
    
    // 读取配置
    const config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
    console.log('[同步] 使用配置', config);
    
    try {
        // 1. 同步员工
        const employeeRes = await fetch(`/api/sync/employees?api_token=${apiToken}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({config: config})
        });
        const employeeData = await employeeRes.json();
        console.log('[同步] 员工数据', employeeData);
        
        // 2. 同步标签
        const tagRes = await fetch(`/api/sync/tags?api_token=${apiToken}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({config: config})
        });
        const tagData = await tagRes.json();
        console.log('[同步] 标签数据', tagData);
        
        // 3. 同步客户
        const customerRes = await fetch(`/api/sync/customers?api_token=${apiToken}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({force: false, config: config})
        });
        const customerData = await customerRes.json();
        console.log('[同步] 客户数据', customerData);
        
        if (customerData.success) {
            showToast(`同步成功！共同步 ${customerData.count} 个客户`, 'success');
            
            // 重新加载数据
            loadEmployees();
            loadTags();
            loadCustomers();
        } else {
            showToast(`同步失败：${customerData.message}`, 'error');
        }
        
    } catch (error) {
        console.error('[同步] 异常', error);
        showToast('同步失败，请检查网络连接或企业微信配置', 'error');
    }
}

// ========== 加载员工列表 ==========
async function loadEmployees() {
    try {
        const res = await fetch(`/api/employees?api_token=${apiToken}`);
        const data = await res.json();
        
        if (data.success) {
            const select = document.getElementById('filter-employee');
            select.innerHTML = '<option value="">全部员工</option>';
            
            data.data.forEach(emp => {
                const option = document.createElement('option');
                option.value = emp.id;
                option.textContent = emp.name;
                select.appendChild(option);
            });
            
            console.log('[员工] 加载成功', data.data.length);
        }
    } catch (error) {
        console.error('[员工] 加载失败', error);
    }
}

// ========== 加载标签列表 ==========
async function loadTags() {
    try {
        const res = await fetch(`/api/tags?api_token=${apiToken}`);
        const data = await res.json();
        
        if (data.success) {
            // 注意：不再需要填充 filter-tag 下拉框，因为我们使用了标签选择器弹窗
            console.log('[标签] 加载成功', data.data.length);
        }
    } catch (error) {
        console.error('[标签] 加载失败', error);
    }
}

// ========== 加载客户列表 ==========
async function loadCustomers() {
    try {
        console.log('[客户] 开始加载客户列表');
        
        // 构建查询参数
        const params = new URLSearchParams({
            api_token: apiToken,
            page: currentPage,
            limit: pageLimit
        });
        
        // 添加筛选条件
        const filterSearch = document.getElementById('filter-search')?.value;
        const filterEmployee = document.getElementById('filter-employee')?.value;
        const filterUserType = document.getElementById('filter-user-type')?.value;
        const filterAddWay = document.getElementById('filter-add-way')?.value;
        const filterDateStart = document.getElementById('filter-date-start')?.value;
        const filterDateEnd = document.getElementById('filter-date-end')?.value;
        const filterGender = document.getElementById('filter-gender')?.value;
        
        console.log('[客户] 筛选条件:', {
            search: filterSearch,
            employee: filterEmployee,
            userType: filterUserType,
            addWay: filterAddWay,
            dateStart: filterDateStart,
            dateEnd: filterDateEnd,
            gender: filterGender,
            tags: selectedTags,
            provinces: selectedProvinces
        });
        
        if (filterSearch) params.append('search', filterSearch);
        if (filterEmployee) params.append('owner_userid', filterEmployee);
        if (filterUserType) params.append('user_type', filterUserType);
        if (filterAddWay) params.append('add_way', filterAddWay);
        if (filterDateStart) params.append('date_start', filterDateStart);
        if (filterDateEnd) params.append('date_end', filterDateEnd);
        if (filterGender) params.append('gender', filterGender);
        
        // 标签筛选
        if (selectedTags && selectedTags.length > 0) {
            params.append('tags', selectedTags.join(','));
        }
        
        // 省份筛选
        if (selectedProvinces && selectedProvinces.length > 0) {
            params.append('provinces', selectedProvinces.join(','));
        }
        
        const url = `/api/customers?${params.toString()}`;
        console.log('[客户] 请求URL:', url);
        
        const res = await fetch(url);
        const data = await res.json();
        
        console.log('[客户] 响应数据:', data);
        
        if (data.success) {
            renderCustomers(data.data);
            updatePagination(data.total, data.page, data.limit);
            
            // 更新筛选结果数量显示
            const resultCount = document.getElementById('filter-result-count');
            if (resultCount) {
                if (data.total > 0) {
                    resultCount.innerHTML = `找到 <strong>${data.total}</strong> 条记录`;
                } else {
                    resultCount.innerHTML = '未找到匹配记录';
                }
            }
            
            console.log('[客户] 加载成功', data.data.length);
        }
    } catch (error) {
        console.error('[客户] 加载失败', error);
        showToast('加载客户列表失败', 'error');
    }
}

// ========== 渲染客户列表 ==========
function renderCustomers(customers) {
    const tbody = document.getElementById('customer-table-body');
    
    if (!customers || customers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 60px 20px; color: var(--grey-500);">
                    <i class="fas fa-users" style="font-size: 48px; margin-bottom: 16px; display: block; opacity: 0.3;"></i>
                    <p style="font-size: 16px; margin-bottom: 8px;">暂无客户数据</p>
                    <p style="font-size: 14px; color: var(--grey-400); margin-bottom: 24px;">
                        点击右上角"同步客户"按钮从企业微信同步客户数据
                    </p>
                    <button class="btn btn-primary" onclick="syncCustomers()">
                        <i class="fas fa-sync-alt"></i> 立即同步
                    </button>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = customers.map(customer => {
        const tags = customer.tags || [];
        const genderText = customer.gender === 1 ? '男' : customer.gender === 2 ? '女' : '未知';
        const genderClass = customer.gender === 1 ? 'badge-male' : customer.gender === 2 ? 'badge-female' : 'badge-unknown';
        const addTime = customer.add_time ? new Date(customer.add_time * 1000).toLocaleString('zh-CN') : '-';
        
        const statusClass = {
            '未跟进': 'status-unfollow',
            '跟进中': 'status-following',
            '已成交': 'status-success',
            '已流失': 'status-lost'
        }[customer.follow_status] || 'status-unfollow';
        
        return `
            <tr>
                <td><input type="checkbox" class="customer-checkbox" value="${customer.id}"></td>
                <td style="text-align: center;">
                    <img src="${customer.avatar || 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2240%22 height=%2240%22%3E%3Crect fill=%22%23ddd%22 width=%2240%22 height=%2240%22/%3E%3Ctext fill=%22%23999%22 font-family=%22sans-serif%22 font-size=%2216%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22%3E头像%3C/text%3E%3C/svg%3E'}" 
                         alt="${customer.name}" 
                         class="customer-avatar"
                         onclick="viewAvatarLarge('${customer.avatar || ''}', '${customer.name}')"
                         onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2240%22 height=%2240%22%3E%3Crect fill=%22%23ddd%22 width=%2240%22 height=%2240%22/%3E%3Ctext fill=%22%23999%22 font-family=%22sans-serif%22 font-size=%2216%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22%3E头像%3C/text%3E%3C/svg%3E'"
                         style="display: inline-block;">
                </td>
                <td>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <span style="font-weight: 600; color: var(--grey-800);">${customer.name || '未知'}</span>
                        <span style="font-size: 12px; color: var(--grey-500);">${customer.corp_name || '暂无企业'}</span>
                    </div>
                </td>
                <td>
                    <span style="color: var(--grey-700);">${customer.remark || '-'}</span>
                </td>
                <td>${customer.owner_name || '-'}</td>
                <td>
                    <span style="color: var(--grey-600); font-size: 13px;">${customer.group_name || '-'}</span>
                </td>
                <td><span class="badge ${genderClass}">${genderText}</span></td>
                <td>
                    <div class="tag-list">
                        ${tags.slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('')}
                        ${tags.length > 3 ? `<span class="tag">+${tags.length - 3}</span>` : ''}
                    </div>
                </td>
                <td>${addTime}</td>
                <td><span class="status-badge ${statusClass}">${customer.follow_status}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-action btn-view" onclick="viewCustomerDetail('${customer.id}')">
                            <i class="fas fa-eye"></i> 查看
                        </button>
                        <button class="btn-action btn-edit" onclick="editCustomerInfo('${customer.id}')">
                            <i class="fas fa-edit"></i> 编辑
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    // 绑定复选框事件
    document.querySelectorAll('.customer-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedCount);
    });
}

// ========== 更新分页 ==========
function updatePagination(total, page, limit) {
    totalCount = total;
    currentPage = page;
    pageLimit = limit;
    totalPages = Math.ceil(total / limit);
    
    document.getElementById('current-page').textContent = currentPage;
    document.getElementById('total-pages').textContent = totalPages;
    document.getElementById('total-count').textContent = totalCount;
}

// ========== 翻页 ==========
function changePage(direction) {
    const newPage = currentPage + direction;
    if (newPage < 1 || newPage > totalPages) return;
    
    currentPage = newPage;
    loadCustomers();
}

// ========== 筛选功能 ==========
function applyFilters() {
    console.log('[筛选] 开始应用筛选条件');
    console.log('[筛选] 选中的标签:', selectedTags);
    console.log('[筛选] 选中的省份:', selectedProvinces);
    currentPage = 1;
    loadCustomers();
}

function filterCustomers() {
    applyFilters();
}

function resetFilters() {
    document.getElementById('filter-search').value = '';
    document.getElementById('filter-employee').value = '';
    document.getElementById('filter-user-type').value = '';
    document.getElementById('filter-add-way').value = '';
    document.getElementById('filter-date-start').value = '';
    document.getElementById('filter-date-end').value = '';
    document.getElementById('filter-gender').value = '';
    
    // 重置标签和省份选择
    selectedTags = [];
    selectedProvinces = [];
    document.getElementById('selected-tags-display').textContent = '企业标签';
    document.getElementById('selected-province-display').textContent = '省份';
    
    applyFilters();
}

// ========== 全选 / 取消全选 ==========
function toggleSelectAll() {
    const selectAll = document.getElementById('select-all').checked;
    document.querySelectorAll('.customer-checkbox').forEach(checkbox => {
        checkbox.checked = selectAll;
    });
    updateSelectedCount();
}

function updateSelectedCount() {
    const checked = document.querySelectorAll('.customer-checkbox:checked');
    selectedCustomers = Array.from(checked).map(cb => cb.value);
    document.getElementById('selected-count').textContent = selectedCustomers.length;
}

// ========== 批量操作 ==========
function batchUpdateOwner() {
    if (selectedCustomers.length === 0) {
        showToast('请先选择客户', 'error');
        return;
    }
    showToast('批量修改跟进人功能开发中...', 'info');
}

function batchUpdateTags() {
    if (selectedCustomers.length === 0) {
        showToast('请先选择客户', 'error');
        return;
    }
    showToast('批量打标签功能开发中...', 'info');
}

function batchSendMessage() {
    if (selectedCustomers.length === 0) {
        showToast('请先选择客户', 'error');
        return;
    }
    showToast('群发消息功能开发中...', 'info');
}

// ========== 客户详情 ==========
function viewCustomer(customerId) {
    console.log('[查看客户]', customerId);
    window.location.href = `/static/customer-detail.html?id=${customerId}`;
}

function editCustomer(customerId) {
    console.log('[编辑客户]', customerId);
    showToast('编辑客户功能开发中...', 'info');
}

function showCustomerDetail(action) {
    showToast('添加客户功能开发中...', 'info');
}

// ========== 导出功能 ==========
async function exportCustomers() {
    // 检查是否选择了客户
    if (selectedCustomers.length === 0) {
        showToast('请先选择要导出的客户', 'warning');
        return;
    }
    
    // 显示导出选项对话框
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h2>导出客户</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
            </div>
            <div class="modal-body">
                <p style="margin-bottom: 20px;">已选择 <strong>${selectedCustomers.length}</strong> 个客户</p>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 10px; font-weight: 500;">
                        导出方式：
                    </label>
                    <div style="display: flex; gap: 10px;">
                        <button class="btn" onclick="exportToExcel()" style="flex: 1;">
                            📄 导出到 Excel
                        </button>
                        <button class="btn btn-primary" onclick="exportToWeComSpreadsheet()" style="flex: 1;">
                            📊 导出到企业微信表格
                        </button>
                    </div>
                </div>
                
                <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6;">
                    <p style="margin: 0; font-size: 14px; color: #1e40af;">
                        <strong>💡 提示：</strong><br>
                        • Excel：下载到本地，适合离线查看<br>
                        • 企业微信表格：在线协作，团队实时共享
                    </p>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// 导出到 Excel
async function exportToExcel() {
    const modal = document.querySelector('.modal');
    if (modal) modal.remove();
    
    showToast('正在生成Excel文件，请稍候...', 'info');
    
    try {
        // 获取当前筛选条件
        const filters = {
            owner_userid: document.getElementById('filter-employee')?.value || '',
            search: document.getElementById('filter-search')?.value || ''
        };
        
        const response = await fetch(`/api/customers/export?api_token=${apiToken}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                customer_ids: selectedCustomers.length > 0 ? selectedCustomers : null,
                filters: filters,
                include_avatar: true  // 包含头像
            })
        });
        
        if (!response.ok) {
            throw new Error(`导出失败: ${response.statusText}`);
        }
        
        // 获取文件名
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = '客户数据.xlsx';
        if (contentDisposition) {
            const matches = /filename=([^;]+)/.exec(contentDisposition);
            if (matches && matches[1]) {
                filename = decodeURIComponent(matches[1]);
            }
        }
        
        // 下载文件
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast(`✅ Excel导出成功！已下载 ${selectedCustomers.length > 0 ? selectedCustomers.length : '全部'} 个客户数据`, 'success');
        
        // 取消选择
        if (selectedCustomers.length > 0) {
            cancelSelection();
        }
    } catch (error) {
        console.error('[导出] 错误:', error);
        showToast('Excel导出失败: ' + error.message, 'error');
    }
}

// 导出到企业微信表格
async function exportToWeComSpreadsheet() {
    const modal = document.querySelector('.modal');
    if (modal) modal.remove();
    
    showToast('正在创建企业微信表格，请稍候...', 'info');
    
    try {
        const config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
        
        const res = await fetch(`/api/export/spreadsheet?api_token=${apiToken}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                customer_ids: selectedCustomers,
                doc_name: `客户列表导出_${new Date().toLocaleString('zh-CN').replace(/[/:]/g, '-')}`,
                admin_users: []  // 可以添加管理员列表
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            // 显示成功对话框
            const successModal = document.createElement('div');
            successModal.className = 'modal active';
            successModal.innerHTML = `
                <div class="modal-content" style="max-width: 500px;">
                    <div class="modal-header">
                        <h2>✅ 导出成功</h2>
                        <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        <div style="text-align: center; padding: 20px;">
                            <div style="font-size: 48px; margin-bottom: 20px;">🎉</div>
                            <p style="font-size: 18px; margin-bottom: 10px;">
                                已成功导出 <strong style="color: #8b5cf6;">${data.count}</strong> 个客户
                            </p>
                            <p style="color: #666; margin-bottom: 30px;">
                                表格已创建，点击下方按钮打开查看
                            </p>
                            
                            <a href="${data.url}" target="_blank" class="btn btn-primary" style="display: inline-block; text-decoration: none; padding: 12px 30px; font-size: 16px;">
                                📊 打开企业微信表格
                            </a>
                            
                            <div style="margin-top: 20px; padding: 15px; background: #f9fafb; border-radius: 8px; text-align: left;">
                                <p style="margin: 0 0 10px 0; font-size: 14px; color: #666;">
                                    <strong>表格链接：</strong>
                                </p>
                                <input type="text" value="${data.url}" readonly 
                                    style="width: 100%; padding: 8px; border: 1px solid #e5e7eb; border-radius: 4px; font-size: 12px; background: white;"
                                    onclick="this.select(); document.execCommand('copy'); showToast('链接已复制', 'success');">
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(successModal);
            
            showToast('导出成功！', 'success');
        } else {
            showToast(`导出失败: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('[导出] 错误:', error);
        showToast('导出失败，请检查网络连接', 'error');
    }
}

// ========== 客户管理辅助功能 ==========

// 同步客户（增量同步 + 进度显示）
async function syncCustomers(force = false) {
    try {
        // 禁用同步按钮，防止重复点击
        const syncButtons = document.querySelectorAll('.btn-sync');
        syncButtons.forEach(btn => {
            btn.disabled = true;
            btn.classList.add('syncing');
        });
        
        // 获取企业微信配置（如果没有配置，后端会使用环境变量的默认值）
        const config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
        
        const syncType = force ? '全量同步' : '增量同步';
        console.log(`[同步客户] 启动${syncType}...`);
        console.log('[同步客户] 配置状态:', {
            has_config: Object.keys(config).length > 0,
            has_corp_id: !!config.corp_id,
            has_secret: !!config.contact_secret
        });
        
        // 全量同步时给出确认提示
        if (force) {
            const confirmed = confirm(
                '⚠️ 全量同步将同步所有客户数据，可能需要较长时间。\n\n' +
                '建议使用"增量同步"仅同步有变化的客户。\n\n' +
                '是否继续全量同步？'
            );
            if (!confirmed) {
                console.log('[同步客户] 用户取消全量同步');
                // 恢复按钮状态
                syncButtons.forEach(btn => {
                    btn.disabled = false;
                    btn.classList.remove('syncing');
                });
                return;
            }
        }
        
        const requestBody = {
            config: Object.keys(config).length > 0 ? config : null,
            force: force  // true = 全量同步, false = 增量同步
        };
        
        console.log('[同步客户] 请求参数:', {
            has_config: requestBody.config !== null,
            force: requestBody.force,
            sync_type: syncType
        });
        
        // 启动同步任务
        const res = await fetch(`/api/sync/customers?api_token=${apiToken}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        console.log('[同步客户] 响应状态:', res.status);
        
        if (!res.ok) {
            const errorText = await res.text();
            console.error('[同步客户] 错误响应:', errorText);
            showToast(`同步失败 (${res.status}): ${errorText}`, 'error');
            // 恢复按钮状态
            syncButtons.forEach(btn => {
                btn.disabled = false;
                btn.classList.remove('syncing');
            });
            return;
        }
        
        const data = await res.json();
        console.log('[同步客户] 响应数据:', data);
        
        if (data.success) {
            // 显示进度对话框
            console.log(`[同步客户] ${syncType}任务已创建，task_id:`, data.task_id);
            showSyncProgressModal(data.task_id, syncType);
        } else {
            showToast(`同步失败: ${data.message}`, 'error');
            console.error('[同步客户] 同步失败:', data);
            // 恢复按钮状态
            syncButtons.forEach(btn => {
                btn.disabled = false;
                btn.classList.remove('syncing');
            });
        }
    } catch (error) {
        console.error('[同步客户] 发生错误:', error);
        console.error('[同步客户] 错误堆栈:', error.stack);
        showToast('同步失败，请检查网络连接和后端服务', 'error');
        // 恢复按钮状态
        const syncButtons = document.querySelectorAll('.btn-sync');
        syncButtons.forEach(btn => {
            btn.disabled = false;
            btn.classList.remove('syncing');
        });
    }
}

// 显示同步进度对话框
let currentSyncTaskId = null;

function showSyncProgressModal(taskId, syncType = '增量同步') {
    currentSyncTaskId = taskId;
    
    // 创建进度对话框
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.id = 'sync-progress-modal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h2>🔄 正在${syncType}客户数据</h2>
                <button class="modal-close" onclick="closeSyncProgressModal()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #666;">×</button>
            </div>
            <div class="modal-body">
                <div style="padding: 20px;">
                    <!-- 进度条 -->
                    <div style="margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span id="sync-progress-text">准备中...</span>
                            <span id="sync-progress-percent">0%</span>
                        </div>
                        <div style="background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div id="sync-progress-bar" style="background: linear-gradient(90deg, #8b5cf6, #a78bfa); height: 100%; width: 0%; transition: width 0.3s;"></div>
                        </div>
                    </div>
                    
                    <!-- 统计信息 -->
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 30px;">
                        <div style="text-align: center; padding: 15px; background: #f9fafb; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: 600; color: #6b7280;" id="sync-total">0</div>
                            <div style="font-size: 12px; color: #9ca3af; margin-top: 4px;">总数</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f0fdf4; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: 600; color: #10b981;" id="sync-added">0</div>
                            <div style="font-size: 12px; color: #6ee7b7; margin-top: 4px;">新增</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #eff6ff; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: 600; color: #3b82f6;" id="sync-updated">0</div>
                            <div style="font-size: 12px; color: #93c5fd; margin-top: 4px;">更新</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #fef2f2; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: 600; color: #ef4444;" id="sync-failed">0</div>
                            <div style="font-size: 12px; color: #fca5a5; margin-top: 4px;">失败</div>
                        </div>
                    </div>
                    
                    <!-- 提示信息 -->
                    <div style="margin-top: 20px; padding: 12px; background: #fef3c7; border-left: 3px solid #f59e0b; border-radius: 4px;">
                        <p style="margin: 0; font-size: 13px; color: #92400e;">
                            💡 采用10线程并发 + 增量同步，仅同步最近变化的客户，大幅提升效率
                        </p>
                    </div>
                    
                    <!-- 停止按钮 -->
                    <div style="margin-top: 20px; text-align: center;">
                        <button onclick="stopSyncTask()" class="btn" style="background: #ef4444; color: white; padding: 10px 30px; border: none; border-radius: 6px; cursor: pointer;">
                            🛑 停止同步
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    // 开始轮询任务状态
    pollSyncProgress(taskId);
}

// 停止同步任务
async function stopSyncTask() {
    if (!currentSyncTaskId) {
        showToast('没有正在运行的同步任务', 'warning');
        return;
    }
    
    if (!confirm('确定要停止同步吗？已同步的数据不会丢失。')) {
        return;
    }
    
    try {
        const res = await fetch(`/api/sync/stop/${currentSyncTaskId}?api_token=${apiToken}`, {
            method: 'POST'
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('正在停止同步...', 'info');
        } else {
            showToast(`停止失败: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('[停止同步] 错误:', error);
        showToast('停止失败，请检查网络连接', 'error');
    }
}

// 关闭进度对话框
function closeSyncProgressModal() {
    if (syncPollInterval) {
        clearInterval(syncPollInterval);
    }
    const modal = document.getElementById('sync-progress-modal');
    if (modal) {
        modal.remove();
    }
    currentSyncTaskId = null;
    
    // 恢复同步按钮状态
    const syncButtons = document.querySelectorAll('.btn-sync');
    syncButtons.forEach(btn => {
        btn.disabled = false;
        btn.classList.remove('syncing');
    });
}

// 轮询同步进度
let syncPollInterval = null;
async function pollSyncProgress(taskId) {
    // 清除之前的轮询
    if (syncPollInterval) {
        clearInterval(syncPollInterval);
    }
    
    // 每秒轮询一次
    syncPollInterval = setInterval(async () => {
        try {
            const res = await fetch(`/api/sync/status/${taskId}?api_token=${apiToken}`);
            const result = await res.json();
            
            if (!result.success) {
                clearInterval(syncPollInterval);
                showToast('获取同步状态失败', 'error');
                return;
            }
            
            const status = result.data;
            
            // 更新UI
            updateSyncProgressUI(status);
            
            // 检查是否完成
            if (status.status === 'completed' || status.status === 'failed') {
                clearInterval(syncPollInterval);
                
                setTimeout(() => {
                    // 关闭进度对话框
                    const modal = document.getElementById('sync-progress-modal');
                    if (modal) {
                        modal.remove();
                    }
                    currentSyncTaskId = null;
                    
                    // 显示结果
                    if (status.status === 'completed') {
                        const duration = Math.round(status.duration);
                        showToast(`✅ 同步完成！新增 ${status.added_count} 个，更新 ${status.updated_count} 个，耗时 ${duration} 秒`, 'success');
                        loadCustomers(); // 重新加载客户列表
                    } else {
                        // 检查是否是用户手动停止
                        if (status.error_message === '用户手动停止') {
                            showToast(`⛔ 同步已停止！已处理 ${status.processed_count} 个客户（新增 ${status.added_count}，更新 ${status.updated_count}）`, 'warning');
                        } else {
                            showToast(`❌ 同步失败: ${status.error_message}`, 'error');
                        }
                        loadCustomers(); // 刷新列表，显示已同步的数据
                    }
                }, 1000);
            }
        } catch (error) {
            console.error('[轮询] 错误:', error);
        }
    }, 1000);
}

// 更新同步进度UI
function updateSyncProgressUI(status) {
    const progressBar = document.getElementById('sync-progress-bar');
    const progressText = document.getElementById('sync-progress-text');
    const progressPercent = document.getElementById('sync-progress-percent');
    const totalEl = document.getElementById('sync-total');
    const addedEl = document.getElementById('sync-added');
    const updatedEl = document.getElementById('sync-updated');
    const failedEl = document.getElementById('sync-failed');
    
    if (!progressBar) return;
    
    // 更新进度条
    progressBar.style.width = `${status.progress}%`;
    progressPercent.textContent = `${status.progress}%`;
    
    // 更新状态文本
    if (status.status === 'running') {
        progressText.textContent = `正在处理：${status.processed_count} / ${status.total_count}`;
    } else if (status.status === 'pending') {
        progressText.textContent = '准备中...';
    }
    
    // 更新统计数字
    totalEl.textContent = status.total_count || 0;
    addedEl.textContent = status.added_count || 0;
    updatedEl.textContent = status.updated_count || 0;
    failedEl.textContent = status.failed_count || 0;
}

// 添加客户
function addCustomer() {
    showToast('添加客户功能开发中...', 'info');
}

// 筛选客户
// 取消选择
function cancelSelection() {
    document.getElementById('select-all').checked = false;
    document.querySelectorAll('.customer-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    selectedCustomers = [];
    document.getElementById('selected-count').textContent = '0';
    document.getElementById('batch-actions').style.display = 'none';
}

// 监听复选框变化，显示/隐藏批量操作栏
document.addEventListener('change', (e) => {
    if (e.target.classList.contains('customer-checkbox')) {
        updateSelectedCount();
        const batchActions = document.getElementById('batch-actions');
        if (batchActions) {
            batchActions.style.display = selectedCustomers.length > 0 ? 'block' : 'none';
        }
    }
});

// ========== 通讯录模块 ==========
let employeesData = [];
let filteredEmployees = [];
let employeePage = 1;
let employeePageLimit = 24;  // 每页显示24个（4列x6行）

// ========== 企业标签管理 ==========
// 同步企业标签
async function syncEnterpriseTags() {
    showToast('正在从企业微信同步标签，请稍候...', 'info');
    
    try {
        const config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
        
        const res = await fetch(`/api/sync/tags?api_token=${apiToken}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ config: config })
        });
        
        if (!res.ok) {
            const errorText = await res.text();
            showToast(`同步失败: ${errorText}`, 'error');
            return;
        }
        
        const data = await res.json();
        
        if (data.success) {
            showToast(`✅ 同步成功！共同步 ${data.count || 0} 个标签组`, 'success');
            loadEnterpriseTagsList();
        } else {
            showToast(`同步失败：${data.message}`, 'error');
        }
        
    } catch (error) {
        console.error('[同步标签] 错误:', error);
        showToast('同步失败，请检查网络连接', 'error');
    }
}

// 加载企业标签列表
async function loadEnterpriseTagsList() {
    console.log('[加载企业标签] 开始');
    try {
        const res = await fetch(`/api/tags?api_token=${apiToken}`);
        console.log('[加载企业标签] 响应状态:', res.status);
        
        const data = await res.json();
        console.log('[加载企业标签] 响应数据:', data);
        
        if (!data.success) {
            showToast('获取标签列表失败', 'error');
            return;
        }
        
        const tagGroups = data.data || [];
        console.log('[加载企业标签] 标签组数量:', tagGroups.length);
        renderEnterpriseTagsList(tagGroups);
        
    } catch (error) {
        console.error('[加载标签] 错误:', error);
        showToast('加载标签列表失败', 'error');
    }
}

// 渲染企业标签列表
function renderEnterpriseTagsList(tagGroups) {
    console.log('[渲染企业标签] 开始, 数据:', tagGroups);
    const container = document.getElementById('tag-groups-container');
    console.log('[渲染企业标签] 容器:', container);
    
    if (!container) {
        console.error('[渲染企业标签] 容器不存在: tag-groups-container');
        return;
    }
    
    if (tagGroups.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 0; color: var(--grey-500);">
                <i class="fas fa-tags" style="font-size: 48px; margin-bottom: 16px; opacity: 0.3;"></i>
                <p>暂无标签数据</p>
                <p style="font-size: 13px;">点击右上角"同步标签"按钮从企业微信同步标签</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = tagGroups.map(group => `
        <div class="tag-group-card" style="margin-bottom: 24px; border: 1px solid var(--grey-300); border-radius: 8px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 style="font-size: 16px; font-weight: 600; color: var(--grey-800); margin: 0;">
                    <i class="fas fa-folder" style="color: var(--primary-main); margin-right: 8px;"></i>
                    ${group.group_name}
                </h3>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-text btn-sm" onclick="editTagGroup('${group.group_id}', '${group.group_name}')">
                        <i class="fas fa-edit"></i> 编辑
                    </button>
                    <button class="btn btn-text btn-sm" style="color: var(--error);" onclick="deleteTagGroup('${group.group_id}')">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                </div>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                ${group.tags.map(tag => `
                    <span class="tag" style="padding: 6px 12px; background: var(--grey-100); color: var(--grey-700); border-radius: 6px; font-size: 13px; cursor: pointer;" onclick="editTag('${tag.tag_id}', '${tag.tag_name}')">
                        ${tag.tag_name}
                    </span>
                `).join('')}
                <button class="btn btn-text btn-sm" onclick="addTagToGroup('${group.group_id}')">
                    <i class="fas fa-plus"></i> 添加标签
                </button>
            </div>
        </div>
    `).join('');
    console.log('[渲染企业标签] 完成');
}

// 添加标签组
function addTagGroup() {
    showToast('该功能需要在企业微信后台创建标签组后同步', 'info');
}

// 编辑标签组
function editTagGroup(groupId, groupName) {
    showToast('该功能需要在企业微信后台修改标签组后同步', 'info');
}

// 删除标签组
function deleteTagGroup(groupId) {
    showToast('该功能需要在企业微信后台删除标签组后同步', 'info');
}

// 添加标签到组
function addTagToGroup(groupId) {
    showToast('该功能需要在企业微信后台添加标签后同步', 'info');
}

// 编辑标签
function editTag(tagId, tagName) {
    showToast('该功能需要在企业微信后台修改标签后同步', 'info');
}

// ========== 企业通讯录管理 ==========
// 同步通讯录
async function syncEmployees() {
    showToast('正在同步通讯录，请稍候...', 'info');
    
    try {
        // 获取企业微信配置
        const config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
        
        console.log('[同步通讯录] 发送配置:', config);
        
        const requestBody = {
            config: config
        };
        
        console.log('[同步通讯录] 请求体:', JSON.stringify(requestBody));
        
        const res = await fetch(`/api/sync/employees?api_token=${apiToken}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        console.log('[同步通讯录] 响应状态:', res.status);
        
        if (!res.ok) {
            const errorText = await res.text();
            console.error('[同步通讯录] 错误响应:', errorText);
            try {
                const errorData = JSON.parse(errorText);
                showToast(`同步失败: ${errorData.detail || errorData.message || '未知错误'}`, 'error');
            } catch {
                showToast(`同步失败 (${res.status}): ${errorText}`, 'error');
            }
            return;
        }
        
        const data = await res.json();
        console.log('[同步通讯录] 响应数据:', data);
        
        if (data.success) {
            showToast(data.message, 'success');
            loadEmployeesList();
        } else {
            showToast(`同步失败：${data.message}`, 'error');
        }
    } catch (error) {
        console.error('[同步通讯录] 异常', error);
        showToast('同步失败，请检查网络连接', 'error');
    }
}

// 加载员工列表
async function loadEmployeesList() {
    try {
        const res = await fetch(`/api/employees?api_token=${apiToken}`);
        const data = await res.json();
        
        if (data.success) {
            // 按本月新增客户数量降序排序
            employeesData = data.data.sort((a, b) => {
                return (b.recent_customer_count || 0) - (a.recent_customer_count || 0);
            });
            filteredEmployees = employeesData;
            renderEmployees();
            console.log('[通讯录] 加载成功', employeesData.length);
        }
    } catch (error) {
        console.error('[通讯录] 加载失败', error);
        showToast('加载通讯录失败', 'error');
    }
}

// 渲染员工卡片
function renderEmployees() {
    const container = document.getElementById('contacts-list');
    
    if (!filteredEmployees || filteredEmployees.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 80px 20px; color: var(--grey-500);">
                <i class="fas fa-address-book" style="font-size: 64px; margin-bottom: 16px; display: block; opacity: 0.3;"></i>
                <p style="font-size: 16px; margin-bottom: 8px;">暂无员工数据</p>
                <p style="font-size: 14px; color: var(--grey-400); margin-bottom: 24px;">
                    点击右上角"同步通讯录"按钮从企业微信同步员工数据
                </p>
                <button class="btn btn-primary" onclick="syncEmployees()">
                    <i class="fas fa-sync-alt"></i> 立即同步
                </button>
            </div>
        `;
        return;
    }
    
    // 分页
    const start = (employeePage - 1) * employeePageLimit;
    const end = start + employeePageLimit;
    const pageData = filteredEmployees.slice(start, end);
    
    container.innerHTML = pageData.map(emp => {
        const department = emp.department ? JSON.parse(emp.department).join(', ') : '未分配';
        
        return `
            <div class="employee-card-new" onclick="viewEmployee('${emp.id}')">
                <!-- 头部：头像 + 基本信息 -->
                <div class="emp-card-header">
                    <div class="emp-avatar-large">
                        ${emp.avatar ? 
                            `<img src="${emp.avatar}" alt="${emp.name}" 
                                 onerror="this.style.display='none'; this.parentElement.innerHTML='<span class=emp-avatar-text>${(emp.name || '?')[0]}</span>'">` 
                            : `<span class="emp-avatar-text">${(emp.name || '?')[0]}</span>`
                        }
                    </div>
                    <div class="emp-card-info">
                        <h3 class="emp-card-name">${emp.name || '未知'}</h3>
                        <div class="emp-card-id">
                            <i class="fas fa-id-card"></i>
                            <span>ID: ${emp.id}</span>
                        </div>
                        <div class="emp-card-dept">
                            <i class="fas fa-building"></i>
                            <span>${department}</span>
                        </div>
                        ${emp.position ? `
                            <div class="emp-card-position">
                                <i class="fas fa-briefcase"></i>
                                <span>${emp.position}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <!-- 联系方式（始终显示） -->
                <div class="emp-contact-primary">
                    ${emp.mobile ? `
                        <div class="emp-contact-main">
                            <i class="fas fa-mobile-alt"></i>
                            <span>${emp.mobile}</span>
                        </div>
                    ` : `
                        <div class="emp-contact-main emp-contact-empty">
                            <i class="fas fa-mobile-alt"></i>
                            <span>暂无手机号</span>
                        </div>
                    `}
                    ${emp.email ? `
                        <div class="emp-contact-main">
                            <i class="fas fa-envelope"></i>
                            <span>${emp.email}</span>
                        </div>
                    ` : `
                        <div class="emp-contact-main emp-contact-empty">
                            <i class="fas fa-envelope"></i>
                            <span>暂无邮箱</span>
                        </div>
                    `}
                </div>
                
                <!-- 统计数据 -->
                <div class="emp-stats-simple">
                    <div class="emp-stat-simple">
                        <div class="emp-stat-value">${emp.customer_count || 0}</div>
                        <div class="emp-stat-label">
                            <i class="fas fa-user-friends"></i>
                            客户总数
                        </div>
                    </div>
                    
                    <div class="emp-stat-simple">
                        <div class="emp-stat-value">${emp.group_count || 0}</div>
                        <div class="emp-stat-label">
                            <i class="fas fa-users"></i>
                            创建群聊
                        </div>
                    </div>
                    
                    <div class="emp-stat-simple">
                        <div class="emp-stat-value">${emp.recent_customer_count || 0}</div>
                        <div class="emp-stat-label">
                            <i class="fas fa-user-plus"></i>
                            本月新增
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // 更新分页
    updateEmployeePagination();
}

// 更新员工分页
function updateEmployeePagination() {
    const totalPages = Math.ceil(filteredEmployees.length / employeePageLimit);
    document.getElementById('employee-current-page').textContent = employeePage;
    document.getElementById('employee-total-pages').textContent = totalPages;
    document.getElementById('employee-total-count').textContent = filteredEmployees.length;
}

// 翻页
function changeEmployeePage(direction) {
    const totalPages = Math.ceil(filteredEmployees.length / employeePageLimit);
    const newPage = employeePage + direction;
    
    if (newPage < 1 || newPage > totalPages) return;
    
    employeePage = newPage;
    renderEmployees();
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 搜索员工
function searchEmployees() {
    const keyword = document.getElementById('employee-search').value.toLowerCase();
    const deptFilter = document.getElementById('employee-dept-filter').value;
    
    filteredEmployees = employeesData.filter(emp => {
        // 关键词搜索
        const matchKeyword = !keyword || 
            emp.name.toLowerCase().includes(keyword) ||
            (emp.mobile && emp.mobile.includes(keyword)) ||
            (emp.email && emp.email.toLowerCase().includes(keyword));
        
        // 部门筛选
        const matchDept = !deptFilter || (emp.department && emp.department.includes(deptFilter));
        
        return matchKeyword && matchDept;
    });
    
    employeePage = 1;
    renderEmployees();
}

// 筛选员工
function filterEmployees() {
    searchEmployees();
}

// 查看员工详情
function viewEmployee(employeeId) {
    console.log('[查看员工]', employeeId);
    showToast('员工详情功能开发中...', 'info');
}

// 导出通讯录
function exportEmployees() {
    showToast('导出功能开发中...', 'info');
}

// 初始化时加载通讯录
if (document.getElementById('module-contacts')) {
    loadEmployeesList();
}

// ========== 智能表格模块 ==========

let currentSpreadsheetId = null;
let uploadedFileData = null;

// 加载表格列表
async function loadSpreadsheetList() {
    try {
        const res = await fetch(`/api/spreadsheet/list?api_token=${apiToken}`);
        const data = await res.json();
        
        if (data.success) {
            renderSpreadsheetList(data.data);
        } else {
            showToast('加载表格列表失败', 'error');
        }
    } catch (error) {
        console.error('[智能表格] 加载列表失败:', error);
        showToast('加载失败，请检查网络连接', 'error');
    }
}

// 渲染表格列表
function renderSpreadsheetList(spreadsheets) {
    const container = document.getElementById('spreadsheet-list');
    
    if (!spreadsheets || spreadsheets.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 20px; color: #666;">
                <i class="fas fa-table" style="font-size: 48px; margin-bottom: 20px; opacity: 0.3;"></i>
                <p style="font-size: 16px;">还没有创建任何表格</p>
                <p style="font-size: 14px; margin-top: 10px;">点击右上角"上传 Excel"按钮创建您的第一个智能表格</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = spreadsheets.map(sheet => {
        const createdDate = new Date(sheet.created_at * 1000).toLocaleString('zh-CN');
        const lastSyncDate = sheet.last_sync_at ? new Date(sheet.last_sync_at * 1000).toLocaleString('zh-CN') : '从未同步';
        
        return `
            <div class="spreadsheet-card" onclick="viewSpreadsheetDetail('${sheet.id}')">
                <div class="spreadsheet-header">
                    <div class="spreadsheet-icon">
                        <i class="fas fa-table"></i>
                    </div>
                    <div class="spreadsheet-info-main">
                        <h3 class="spreadsheet-title">${sheet.name}</h3>
                        <div class="spreadsheet-meta">
                            <span><i class="fas fa-th"></i> ${sheet.col_count} 字段</span>
                            <span><i class="fas fa-list"></i> ${sheet.row_count} 行</span>
                            <span><i class="fas fa-clock"></i> ${createdDate}</span>
                        </div>
                    </div>
                </div>
                <div class="spreadsheet-footer">
                    <span class="last-sync">最后同步: ${lastSyncDate}</span>
                    <div class="spreadsheet-actions" onclick="event.stopPropagation();">
                        <button class="btn-icon" onclick="openSpreadsheetInWecom('${sheet.url}')" title="在企业微信中打开">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                        <button class="btn-icon" onclick="syncSpreadsheetById('${sheet.id}')" title="同步数据">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// 显示上传 Excel 对话框
function showUploadExcelDialog() {
    console.log('[调试] showUploadExcelDialog 被调用');
    const modal = document.getElementById('upload-excel-modal');
    if (modal) {
        modal.classList.add('show');  // 改为 'show' 而不是 'active'
        console.log('[调试] 对话框已显示');
    } else {
        console.error('[调试] 找不到 upload-excel-modal 元素');
        return;
    }
    const previewArea = document.getElementById('excel-preview-area');
    if (previewArea) {
        previewArea.style.display = 'none';
    }
    uploadedFileData = null;
}

// 关闭上传对话框
function closeUploadExcelDialog() {
    console.log('[调试] closeUploadExcelDialog 被调用');
    const modal = document.getElementById('upload-excel-modal');
    if (modal) {
        modal.classList.remove('show');  // 改为 'show' 而不是 'active'
    }
    
    // 隐藏预览区域和按钮
    document.getElementById('excel-preview-area').style.display = 'none';
    document.getElementById('excel-modal-footer').style.display = 'none';
    
    // 清空文件输入
    const fileInput = document.getElementById('excel-file-input');
    if (fileInput) {
        fileInput.value = '';
    }
    uploadedFileData = null;
}

// 处理文件选择
async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    showToast('正在解析 Excel 文件...', 'info');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const res = await fetch(`/api/spreadsheet/upload?api_token=${apiToken}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await res.json();
        
        if (data.success) {
            uploadedFileData = data;
            showExcelPreview(data);
            showToast('Excel 解析成功！', 'success');
        } else {
            showToast(`解析失败: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('[上传] Excel 解析失败:', error);
        showToast('解析失败，请检查文件格式', 'error');
    }
}

// 显示 Excel 预览
function showExcelPreview(data) {
    document.getElementById('excel-preview-area').style.display = 'block';
    document.getElementById('excel-modal-footer').style.display = 'flex';  // 显示按钮区域
    
    // 设置默认表格名称（使用简单格式，避免特殊字符）
    const now = new Date();
    const timestamp = `${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}`;
    const filename = data.file_name.replace(/\.[^/.]+$/, '').replace(/[_\-]/g, '');
    document.getElementById('spreadsheet-name').value = `${filename}${timestamp}`;
    
    // 渲染预览表格
    const table = `
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f9fafb;">
                    ${data.headers.map(h => `<th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb; font-weight: 600;">${h}</th>`).join('')}
                </tr>
            </thead>
            <tbody>
                ${data.data.slice(0, 5).map(row => `
                    <tr style="border-bottom: 1px solid #f3f4f6;">
                        ${row.map(cell => `<td style="padding: 12px;">${cell}</td>`).join('')}
                    </tr>
                `).join('')}
                ${data.row_count > 5 ? `
                    <tr>
                        <td colspan="${data.col_count}" style="padding: 12px; text-align: center; color: #666; font-size: 14px;">
                            ... 还有 ${data.row_count - 5} 行数据
                        </td>
                    </tr>
                ` : ''}
            </tbody>
        </table>
    `;
    
    document.getElementById('excel-preview-table').innerHTML = table;
    document.getElementById('excel-info').innerHTML = `
        文件名: ${data.file_name} | 共 ${data.row_count} 行，${data.col_count} 列
    `;
}

// 从 Excel 创建表格
async function createSpreadsheetFromExcel() {
    if (!uploadedFileData) {
        showToast('请先上传 Excel 文件', 'warning');
        return;
    }
    
    const name = document.getElementById('spreadsheet-name').value.trim();
    if (!name) {
        showToast('请输入表格名称', 'warning');
        return;
    }
    
    showToast('正在创建企业微信表格...', 'info');
    
    try {
        // 获取企业微信配置
        const config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
        
        const fields = uploadedFileData.headers.map(header => ({
            name: header,
            type: uploadedFileData.field_types[header] || 'text'
        }));
        
        const res = await fetch(`/api/spreadsheet/create?api_token=${apiToken}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                fields: fields,
                data: uploadedFileData.data,
                config: config
                // 临时移除 admin_users 测试
                // admin_users: ['19938885888']
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            // 根据成功类型显示不同的消息
            if (data.success_type === 'partial' || !data.data_written) {
                // 部分成功：表格创建了但数据没写入
                showToast('表格创建成功！', 'success');
                closeUploadExcelDialog();
                loadSpreadsheetList();
                
                // 显示警告信息和导入提示
                setTimeout(() => {
                    const message = data.message + '\n\n建议：\n1. 点击"打开查看"在企业微信中查看表格\n2. 手动复制粘贴数据到表格中\n或\n3. 在企业微信中导入 Excel 文件\n\n是否现在打开查看？';
                    if (confirm(message)) {
                        window.open(data.url, '_blank');
                    }
                }, 500);
            } else {
                // 完全成功：表格创建且数据写入成功
                showToast('表格创建成功！', 'success');
                closeUploadExcelDialog();
                loadSpreadsheetList();
                
                // ⭐ 显示优化提示弹窗
                setTimeout(() => {
                    showOptimizationTip({
                        doc_name: name,
                        url: data.url,
                        field_count: data.field_count || uploadedFileData.headers.length,
                        record_count: data.record_count || uploadedFileData.data.length,
                        empty_columns: data.empty_columns || [],
                        optimization_tip: data.optimization_tip || false
                    });
                }, 500);
            }
        } else {
            // 检查配置
            const config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
            const hasConfig = config.corpid && (config.app_secret || config.customer_secret || config.contact_secret);
            
            if (data.message && data.message.includes('invalid corpid')) {
                if (hasConfig) {
                    // 已配置但企业ID错误
                    showToast('企业ID验证失败，请检查企业ID是否正确', 'error');
                    setTimeout(() => {
                        if (confirm('企业ID可能有误，是否重新配置？\n\n提示：请从企业微信后台重新复制企业ID')) {
                            showConfig();
                        }
                    }, 3000);
                } else {
                    // 未配置
                    showToast('请先配置企业微信凭证！点击右上角"配置"按钮', 'error');
                    setTimeout(() => {
                        if (confirm('是否现在配置企业微信凭证？')) {
                            showConfig();
                        }
                    }, 3000);
                }
            } else if (data.message && data.message.includes('access_token missing')) {
                // access_token 缺失
                showToast('请先配置企业微信凭证！点击右上角"配置"按钮', 'error');
                setTimeout(() => {
                    if (confirm('是否现在配置企业微信凭证？')) {
                        showConfig();
                    }
                }, 3000);
            } else {
                // 其他错误
                showToast(`创建失败: ${data.message}`, 'error');
            }
        }
    } catch (error) {
        console.error('[创建表格] 失败:', error);
        showToast('创建失败，请检查网络连接', 'error');
    }
}

// 查看表格详情
async function viewSpreadsheetDetail(spreadsheetId) {
    currentSpreadsheetId = spreadsheetId;
    
    try {
        const res = await fetch(`/api/spreadsheet/${spreadsheetId}?api_token=${apiToken}`);
        const data = await res.json();
        
        if (data.success) {
            showSpreadsheetDetailModal(data.data);
        } else {
            showToast('加载表格详情失败', 'error');
        }
    } catch (error) {
        console.error('[表格详情] 加载失败:', error);
        showToast('加载失败，请检查网络连接', 'error');
    }
}

// 显示表格详情对话框
function showSpreadsheetDetailModal(spreadsheet) {
    document.getElementById('spreadsheet-detail-title').textContent = spreadsheet.name;
    
    const createdDate = new Date(spreadsheet.created_at * 1000).toLocaleString('zh-CN');
    const lastSyncDate = spreadsheet.last_sync_at ? new Date(spreadsheet.last_sync_at * 1000).toLocaleString('zh-CN') : '从未同步';
    
    const infoHtml = `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; padding: 15px; background: #f9fafb; border-radius: 8px; margin-bottom: 20px;">
            <div><strong>表格名称:</strong> ${spreadsheet.name}</div>
            <div><strong>文档 ID:</strong> ${spreadsheet.docid}</div>
            <div><strong>字段数量:</strong> ${spreadsheet.col_count} 个</div>
            <div><strong>数据行数:</strong> ${spreadsheet.row_count} 行</div>
            <div><strong>创建时间:</strong> ${createdDate}</div>
            <div><strong>最后同步:</strong> ${lastSyncDate}</div>
            <div><strong>版本:</strong> v${spreadsheet.version}</div>
            <div><strong>状态:</strong> <span class="badge badge-success">${spreadsheet.status === 'active' ? '正常' : '已归档'}</span></div>
        </div>
    `;
    
    document.getElementById('spreadsheet-info').innerHTML = infoHtml;
    
    // 渲染数据表格
    if (spreadsheet.fields && spreadsheet.fields.length > 0) {
        const headers = spreadsheet.fields.map(f => f.name);
        const tableHtml = `
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f9fafb;">
                        ${headers.map(h => `<th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb; font-weight: 600;">${h}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${(spreadsheet.data || []).slice(0, 10).map(row => `
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            ${row.map(cell => `<td style="padding: 12px;">${cell || '-'}</td>`).join('')}
                        </tr>
                    `).join('')}
                    ${spreadsheet.data && spreadsheet.data.length > 10 ? `
                        <tr>
                            <td colspan="${headers.length}" style="padding: 12px; text-align: center; color: #666; font-size: 14px;">
                                ... 还有 ${spreadsheet.data.length - 10} 行数据
                            </td>
                        </tr>
                    ` : ''}
                </tbody>
            </table>
        `;
        document.getElementById('spreadsheet-data-table').innerHTML = tableHtml;
    }
    
    document.getElementById('spreadsheet-detail-modal').classList.add('show');
}

// 关闭表格详情
function closeSpreadsheetDetail() {
    document.getElementById('spreadsheet-detail-modal').classList.remove('show');
    currentSpreadsheetId = null;
}

// 同步表格数据
async function syncSpreadsheet() {
    if (!currentSpreadsheetId) return;
    
    showToast('正在同步数据...', 'info');
    
    try {
        // 获取企业微信配置
        const config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
        
        const res = await fetch(`/api/spreadsheet/${currentSpreadsheetId}/sync?api_token=${apiToken}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                config: config
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            if (data.changed) {
                showToast(`同步成功！更新了 ${data.row_count} 行数据`, 'success');
                // 重新加载详情
                setTimeout(() => {
                    viewSpreadsheetDetail(currentSpreadsheetId);
                }, 1000);
            } else {
                showToast('数据已是最新，无需更新', 'info');
            }
        } else {
            showToast(`同步失败: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('[同步] 失败:', error);
        showToast('同步失败，请检查网络连接', 'error');
    }
}

// 通过 ID 同步表格
async function syncSpreadsheetById(spreadsheetId) {
    currentSpreadsheetId = spreadsheetId;
    await syncSpreadsheet();
    loadSpreadsheetList();
}

// 在企业微信中打开
function openInWecom() {
    const url = document.getElementById('spreadsheet-info').closest('.modal-body').querySelector('[href]')?.href;
    if (url) {
        window.open(url, '_blank');
    }
}

// 打开企业微信表格
function openSpreadsheetInWecom(url) {
    if (url) {
        window.open(url, '_blank');
    } else {
        showToast('表格链接不可用', 'warning');
    }
}

// ========== 手工创建表格功能 ==========

// 全局变量：当前字段列表
let currentFields = [];
let templateList = [];
let supplierList = [];

// 显示手工创建表格对话框
function showCreateTableDialog() {
    console.log('[创建表格] 打开手工创建对话框');
    
    // 重置表单
    document.getElementById('table-name').value = '';
    document.getElementById('table-data-type').value = 'order';
    document.getElementById('table-data-scope').value = 'global';
    document.getElementById('supplier-select-group').style.display = 'none';
    currentFields = [];
    updateFieldsList();
    
    // 加载供应商列表
    loadSupplierList();
    
    // 显示对话框
    document.getElementById('create-table-modal').style.display = 'flex';
}

// 关闭手工创建表格对话框
function closeCreateTableDialog() {
    document.getElementById('create-table-modal').style.display = 'none';
}

// 数据类型改变
function onDataTypeChange() {
    const dataType = document.getElementById('table-data-type').value;
    console.log('[创建表格] 数据类型改变:', dataType);
}

// 数据范围改变
function onDataScopeChange() {
    const scope = document.getElementById('table-data-scope').value;
    const supplierGroup = document.getElementById('supplier-select-group');
    
    if (scope === 'supplier') {
        supplierGroup.style.display = 'block';
    } else {
        supplierGroup.style.display = 'none';
    }
}

// 加载供应商列表
async function loadSupplierList() {
    try {
        const res = await fetch(`/api/suppliers/list?api_token=${apiToken}`);
        const data = await res.json();
        
        if (data.success) {
            supplierList = data.data;
            
            const select = document.getElementById('table-supplier-code');
            select.innerHTML = supplierList.map(s => 
                `<option value="${s.code}">${s.name}</option>`
            ).join('');
        }
    } catch (error) {
        console.error('[创建表格] 加载供应商列表失败:', error);
    }
}

// 显示模板选择器
async function showTemplateSelector() {
    try {
        const res = await fetch(`/api/templates/list?api_token=${apiToken}`);
        const data = await res.json();
        
        if (data.success) {
            templateList = data.data;
            
            const templateListEl = document.getElementById('template-list');
            templateListEl.innerHTML = templateList.map(t => `
                <div class="template-item" style="padding: 15px; margin-bottom: 10px; border: 1px solid #e5e7eb; border-radius: 8px; cursor: pointer;"
                     onclick="selectTemplate('${t.id}')">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0 0 5px 0;">${t.name}</h4>
                            <p style="margin: 0; font-size: 14px; color: #666;">${t.description || ''}</p>
                        </div>
                        ${t.is_system ? '<span style="background: #8b5cf6; color: white; padding: 3px 10px; border-radius: 12px; font-size: 12px;">系统模板</span>' : ''}
                    </div>
                </div>
            `).join('');
            
            document.getElementById('template-selector-modal').style.display = 'flex';
        }
    } catch (error) {
        console.error('[创建表格] 加载模板失败:', error);
        showToast('加载模板失败', 'error');
    }
}

// 关闭模板选择器
function closeTemplateSelector() {
    document.getElementById('template-selector-modal').style.display = 'none';
}

// 选择模板
async function selectTemplate(templateId) {
    try {
        const res = await fetch(`/api/templates/${templateId}?api_token=${apiToken}`);
        const data = await res.json();
        
        if (data.success) {
            // 将模板字段添加到当前字段列表
            currentFields = [...data.data.fields];
            
            // 调试：检查字段是否包含 editable 属性
            console.log('[模板导入] 字段数量:', currentFields.length);
            console.log('[模板导入] 前3个字段:', currentFields.slice(0, 3));
            
            updateFieldsList();
            closeTemplateSelector();
            showToast(`已导入 ${currentFields.length} 个字段`, 'success');
        }
    } catch (error) {
        console.error('[创建表格] 选择模板失败:', error);
        showToast('选择模板失败', 'error');
    }
}

// 显示添加字段对话框
function showAddFieldDialog() {
    if (currentFields.length >= 150) {
        showToast('字段数量已达上限（150个）', 'warning');
        return;
    }
    
    document.getElementById('field-wecom-name').value = '';
    document.getElementById('field-system-name').value = '';
    document.getElementById('field-type').value = 'text';
    document.getElementById('add-field-modal').style.display = 'flex';
}

// 关闭添加字段对话框
function closeAddFieldDialog() {
    document.getElementById('add-field-modal').style.display = 'none';
}

// 添加字段到列表
function addFieldToList() {
    const wecomName = document.getElementById('field-wecom-name').value.trim();
    const systemName = document.getElementById('field-system-name').value.trim();
    const type = document.getElementById('field-type').value;
    
    if (!wecomName) {
        showToast('请输入字段显示名称', 'warning');
        return;
    }
    
    if (!systemName) {
        showToast('请输入系统字段名', 'warning');
        return;
    }
    
    // 检查重复
    if (currentFields.some(f => f.wecom_name === wecomName)) {
        showToast('字段名称已存在', 'warning');
        return;
    }
    
    // 添加字段，默认不可编辑
    currentFields.push({
        wecom_name: wecomName,
        system_name: systemName,
        type: type,
        editable: false  // 默认不可编辑
    });
    
    updateFieldsList();
    closeAddFieldDialog();
    showToast('字段添加成功', 'success');
}

// 更新字段列表显示
function updateFieldsList() {
    const listEl = document.getElementById('fields-list');
    const badge = document.getElementById('field-count-badge');
    
    badge.textContent = `(${currentFields.length}/150)`;
    
    if (currentFields.length === 0) {
        listEl.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #9ca3af;">
                <i class="fas fa-list" style="font-size: 48px; margin-bottom: 10px;"></i>
                <p>还没有字段，请添加或从模板导入</p>
            </div>
        `;
    } else {
        listEl.innerHTML = currentFields.map((field, index) => {
            // 安全获取 editable 属性，如果不存在则默认为 false
            const editable = field.editable === true;
            const editableIcon = editable ? '✏️' : '🔒';
            const editableText = editable ? '可编辑' : '只读';
            const editableColor = editable ? '#10b981' : '#ef4444';
            const editableBg = editable ? '#d1fae5' : '#fee2e2';
            
            return `
            <div class="field-item" style="padding: 12px; margin-bottom: 8px; background: white; border: 1px solid #e5e7eb; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                        <strong>${field.wecom_name}</strong>
                        <span style="color: #9ca3af;">→</span>
                        <span style="color: #666;">${field.system_name}</span>
                        <span style="font-size: 12px; color: #8b5cf6; background: #f3f4f6; padding: 2px 8px; border-radius: 4px;">${field.type}</span>
                        <button onclick="toggleEditable(${index})" style="border: none; background: ${editableBg}; color: ${editableColor}; padding: 4px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; display: flex; align-items: center; gap: 5px; font-weight: 500;" title="点击切换编辑权限">
                            <span>${editableIcon}</span>
                            <span>${editableText}</span>
                        </button>
                    </div>
                </div>
                <div style="display: flex; gap: 5px;">
                    <button class="btn-icon" onclick="moveFieldUp(${index})" ${index === 0 ? 'disabled' : ''} title="上移">
                        <i class="fas fa-arrow-up"></i>
                    </button>
                    <button class="btn-icon" onclick="moveFieldDown(${index})" ${index === currentFields.length - 1 ? 'disabled' : ''} title="下移">
                        <i class="fas fa-arrow-down"></i>
                    </button>
                    <button class="btn-icon btn-danger" onclick="removeField(${index})" title="删除">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `}).join('');
    }
}

// 移动字段位置（上）
function moveFieldUp(index) {
    if (index === 0) return;
    [currentFields[index], currentFields[index - 1]] = [currentFields[index - 1], currentFields[index]];
    updateFieldsList();
}

// 移动字段位置（下）
function moveFieldDown(index) {
    if (index === currentFields.length - 1) return;
    [currentFields[index], currentFields[index + 1]] = [currentFields[index + 1], currentFields[index]];
    updateFieldsList();
}

// 删除字段
function removeField(index) {
    currentFields.splice(index, 1);
    updateFieldsList();
}

// 切换字段编辑权限
function toggleEditable(index) {
    if (currentFields[index]) {
        currentFields[index].editable = !currentFields[index].editable;
        updateFieldsList();
        
        const field = currentFields[index];
        const status = field.editable ? '可编辑' : '只读';
        showToast(`已将"${field.wecom_name}"设置为${status}`, 'success');
    }
}

// 手工创建表格
async function createTableManual() {
    const name = document.getElementById('table-name').value.trim();
    const dataType = document.getElementById('table-data-type').value;
    const dataScope = document.getElementById('table-data-scope').value;
    const supplierCode = document.getElementById('table-supplier-code').value;
    
    // 验证
    if (!name) {
        showToast('请输入表格名称', 'warning');
        return;
    }
    
    if (currentFields.length === 0) {
        showToast('请至少添加一个字段', 'warning');
        return;
    }
    
    if (dataScope === 'supplier' && !supplierCode) {
        showToast('请选择供应商', 'warning');
        return;
    }
    
    try {
        console.log('[创建表格] 开始创建:', name, dataType, dataScope, supplierCode);
        console.log('[创建表格] 字段数量:', currentFields.length);
        console.log('[创建表格] 字段列表:', currentFields);
        
        const wecomConfig = JSON.parse(localStorage.getItem('wecom_config') || '{}');
        
        const requestData = {
            name,
            data_type: dataType,
            data_scope: dataScope,
            supplier_code: dataScope === 'supplier' ? supplierCode : null,
            fields: currentFields,
            config: wecomConfig
        };
        
        const res = await fetch(`/api/spreadsheet/create-manual?api_token=${apiToken}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('表格创建成功！', 'success');
            closeCreateTableDialog();
            
            // 刷新表格列表
            loadSpreadsheetList();
            
            // 显示字段权限说明（如果有只读字段）
            const fieldNote = data.data.field_usage_note;
            if (fieldNote && fieldNote.readonly_count > 0) {
                setTimeout(() => {
                    const noteMsg = `📋 字段权限说明：\n\n` +
                        `• 总字段数：${fieldNote.total_fields}\n` +
                        `• 只读字段：${fieldNote.readonly_count} 个\n` +
                        `• 可编辑字段：${fieldNote.editable_count} 个\n\n` +
                        `⚠️ 提示：由于企业微信 API 限制，无法通过接口设置字段为只读。\n` +
                        `请在企业微信中手动避免编辑标记为"只读"的字段。\n\n` +
                        `只读字段列表（前10个）：\n${fieldNote.readonly_fields.slice(0, 10).join('、')}`;
                    
                    alert(noteMsg);
                }, 300);
            }
            
            // 询问是否在企业微信中打开
            setTimeout(() => {
                if (confirm('表格已创建成功！是否在企业微信中打开查看？')) {
                    window.open(data.data.url, '_blank');
                }
            }, fieldNote && fieldNote.readonly_count > 0 ? 1500 : 500);
        } else {
            showToast(`创建失败：${data.message}`, 'error');
            
            // 检查是否是配置问题
            if (data.message.includes('invalid corpid') || data.message.includes('access_token')) {
                setTimeout(() => {
                    if (confirm('企业微信配置可能有误，是否重新配置？')) {
                        showConfig();
                    }
                }, 500);
            }
        }
    } catch (error) {
        console.error('[创建表格] 失败:', error);
        showToast('网络错误，请重试', 'error');
    }
}

// 删除表格
async function deleteSpreadsheet() {
    if (!currentSpreadsheetId) return;
    
    if (!confirm('确定要删除这个表格吗？此操作不可恢复。')) {
        return;
    }
    
    try {
        const res = await fetch(`/api/spreadsheet/${currentSpreadsheetId}?api_token=${apiToken}`, {
            method: 'DELETE'
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('表格已删除', 'success');
            closeSpreadsheetDetail();
            loadSpreadsheetList();
        } else {
            showToast(`删除失败: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('[删除] 失败:', error);
        showToast('删除失败，请检查网络连接', 'error');
    }
}

// 模块切换时加载对应数据
document.addEventListener('DOMContentLoaded', () => {
    // 监听模块切换
    const originalSwitchModule = window.switchModule;
    window.switchModule = function(moduleName) {
        if (originalSwitchModule) {
            originalSwitchModule(moduleName);
        }
        
        // 切换到智能表格模块时加载列表
        if (moduleName === 'spreadsheet') {
            loadSpreadsheetList();
        }
    };
});

// ========== 优化提示弹窗 ==========

// 显示优化提示弹窗
function showOptimizationTip(result) {
    console.log('[优化提示] 收到结果:', result);
    
    // 检查是否需要提示
    if (!result.optimization_tip) {
        console.log('[优化提示] 无需优化提示，直接打开表格');
        // 无空白列，直接打开表格
        if (result.url && confirm('表格已创建并写入数据！是否在企业微信中打开查看？')) {
            window.open(result.url, '_blank');
        }
        return;
    }
    
    // 检查用户是否选择了"不再提示"
    const hideOptimizationTip = localStorage.getItem('hideOptimizationTip');
    if (hideOptimizationTip === 'true') {
        console.log('[优化提示] 用户选择了不再提示');
        // 用户选择了不再提示，直接打开表格
        if (result.url) {
            window.open(result.url, '_blank');
        }
        return;
    }
    
    const emptyColumns = result.empty_columns || [];
    const emptyColumnNames = emptyColumns.map(c => c.field_title).join('、');
    
    console.log('[优化提示] 显示优化弹窗，空白列:', emptyColumnNames);
    
    const modalHtml = `
        <div class="optimization-modal-overlay" onclick="closeOptimizationModal(event)">
            <div class="optimization-modal" onclick="event.stopPropagation()">
                <div class="optimization-modal-header">
                    <h3>📊 表格导入成功！</h3>
                    <button class="modal-close-btn" onclick="closeOptimizationModal()">&times;</button>
                </div>
                <div class="optimization-modal-body">
                    <div class="info-section">
                        <p><strong>表格名称:</strong> ${result.doc_name}</p>
                        <p><strong>字段数量:</strong> ${result.field_count} 个</p>
                        <p><strong>记录数量:</strong> ${result.record_count} 条</p>
                    </div>
                    
                    <div class="tip-box">
                        <h4>💡 优化建议</h4>
                        <p>检测到 <strong>${emptyColumns.length}</strong> 个空白列(<strong>${emptyColumnNames}</strong>)，建议进行以下优化：</p>
                        
                        <div class="optimization-options">
                            <div class="option">
                                <div class="option-header">
                                    <span class="option-number">1</span>
                                    <h5>隐藏空白列</h5>
                                </div>
                                <ol>
                                    <li>打开智能表格</li>
                                    <li>右键点击列标题（<strong>${emptyColumnNames}</strong>）</li>
                                    <li>选择 <strong>"隐藏列"</strong></li>
                                    <li>重复操作隐藏所有空白列</li>
                                </ol>
                            </div>
                            
                            <div class="option">
                                <div class="option-header">
                                    <span class="option-number">2</span>
                                    <h5>调整列顺序</h5>
                                </div>
                                <ol>
                                    <li>打开智能表格</li>
                                    <li>点击并按住列标题</li>
                                    <li>拖动到合适的位置</li>
                                    <li>将常用列放在前面</li>
                                </ol>
                            </div>
                        </div>
                        
                        <div class="tip-note">
                            <strong>💬 提示:</strong> 这些空白列是企业微信智能表格的默认字段，无法通过API删除，但不影响数据使用。
                        </div>
                    </div>
                    
                    <div class="checkbox-container">
                        <label>
                            <input type="checkbox" id="dontShowAgain">
                            不再提示此优化建议
                        </label>
                    </div>
                </div>
                <div class="optimization-modal-footer">
                    <button class="btn-secondary" onclick="closeOptimizationModal()">
                        知道了
                    </button>
                    <button class="btn-primary" onclick="openSmartsheetAndClose('${result.url}')">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                            <polyline points="15 3 21 3 21 9"></polyline>
                            <line x1="10" y1="14" x2="21" y2="3"></line>
                        </svg>
                        打开表格
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// 关闭优化提示弹窗
function closeOptimizationModal(event) {
    // 如果是点击背景层，检查是否点击的是背景而不是弹窗内容
    if (event && event.target.classList.contains('optimization-modal')) {
        return;
    }
    
    const dontShowAgainCheckbox = document.getElementById('dontShowAgain');
    if (dontShowAgainCheckbox && dontShowAgainCheckbox.checked) {
        localStorage.setItem('hideOptimizationTip', 'true');
        console.log('[优化提示] 用户选择了不再提示');
    }
    
    const modal = document.querySelector('.optimization-modal-overlay');
    if (modal) {
        modal.remove();
    }
}

// 打开表格并关闭弹窗
function openSmartsheetAndClose(url) {
    if (url) {
        window.open(url, '_blank');
    }
    closeOptimizationModal();
}

// 导航折叠
function toggleNavGroup(event, groupId) {
    event.preventDefault();
    event.stopPropagation();
    
    const toggleBtn = event.target.closest('.nav-group-toggle');
    const navGroup = toggleBtn.closest('.nav-group');
    
    // 关闭所有其他导航组
    document.querySelectorAll('.nav-group').forEach(g => {
        if (g !== navGroup) {
            g.classList.remove('open');
        }
    });
    
    // 切换当前组
    navGroup.classList.toggle('open');
    
    // 防止冒泡到导航点击事件
    return false;
}

// ========== 暴露全局函数（用于 HTML onclick） ==========
// 通用
window.syncData = syncData;
window.showToast = showToast;
window.toggleNavGroup = toggleNavGroup;
window.switchModule = switchModule;

// 查看头像大图
function viewAvatarLarge(avatarUrl, customerName) {
    if (!avatarUrl) {
        showToast('暂无头像', 'info');
        return;
    }
    
    // 创建大图查看器
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.id = 'avatar-viewer-modal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px; background: transparent; box-shadow: none;">
            <div style="position: relative;">
                <button onclick="closeAvatarViewer()" 
                        style="position: absolute; top: -40px; right: 0; background: rgba(0,0,0,0.5); color: white; border: none; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; font-size: 20px; display: flex; align-items: center; justify-content: center;">
                    ×
                </button>
                <img src="${avatarUrl}" 
                     alt="${customerName}" 
                     style="width: 100%; max-width: 500px; border-radius: 8px; display: block; margin: 0 auto;">
                <div style="text-align: center; color: white; margin-top: 16px; font-size: 14px; text-shadow: 0 1px 3px rgba(0,0,0,0.8);">
                    ${customerName}
                </div>
            </div>
        </div>
    `;
    
    // 点击背景关闭
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeAvatarViewer();
        }
    });
    
    document.body.appendChild(modal);
}

// 关闭头像查看器
function closeAvatarViewer() {
    const modal = document.getElementById('avatar-viewer-modal');
    if (modal) {
        modal.remove();
    }
}

// 查看客户详情（弹窗显示完整资料）
async function viewCustomerDetail(customerId) {
    try {
        showToast('正在加载客户详情...', 'info');
        
        // 获取客户详情
        const res = await fetch(`/api/customers/${customerId}?api_token=${apiToken}`);
        const data = await res.json();
        
        if (!data.success) {
            showToast('获取客户详情失败', 'error');
            return;
        }
        
        const customer = data.data;
        
        // 解析标签
        let enterpriseTags = [];
        let personalTags = [];
        let ruleTags = [];
        
        try {
            if (customer.enterprise_tags) {
                enterpriseTags = JSON.parse(customer.enterprise_tags);
            }
            if (customer.personal_tags) {
                personalTags = JSON.parse(customer.personal_tags);
            }
            if (customer.rule_tags) {
                ruleTags = JSON.parse(customer.rule_tags);
            }
        } catch (e) {
            console.error('解析标签失败:', e);
        }
        
        // 格式化字段
        const genderMap = { 0: '未知', 1: '男', 2: '女' };
        const addWayMap = {
            0: '未知', 1: '扫码', 2: '搜索手机号', 3: '名片分享', 4: '群聊',
            5: '手机通讯录', 6: '微信联系人', 7: '来自微信', 8: '安装应用',
            9: '搜索邮箱', 201: '内部成员共享', 202: '管理员分配'
        };
        
        const addTime = customer.add_time ? new Date(customer.add_time * 1000).toLocaleString('zh-CN') : '-';
        const createdAt = customer.created_at ? new Date(customer.created_at * 1000).toLocaleString('zh-CN') : '-';
        const updatedAt = customer.updated_at ? new Date(customer.updated_at * 1000).toLocaleString('zh-CN') : '-';
        
        // 创建详情弹窗
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.id = 'customer-detail-modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 800px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header" style="border-bottom: 1px solid #e5e7eb; padding-bottom: 16px;">
                    <h2 style="display: flex; align-items: center; gap: 12px;">
                        <img src="${customer.avatar || 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2240%22 height=%2240%22%3E%3Crect fill=%22%23ddd%22 width=%2240%22 height=%2240%22/%3E%3C/svg%3E'}" 
                             style="width: 48px; height: 48px; border-radius: 8px; object-fit: cover;">
                        <span>${customer.name || '未知客户'}</span>
                    </h2>
                    <button class="modal-close" onclick="closeCustomerDetail()">×</button>
                </div>
                <div class="modal-body" style="padding: 24px;">
                    <!-- 基础信息 -->
                    <div style="margin-bottom: 24px;">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--grey-800);">📋 基础信息</h3>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                            <div class="detail-item">
                                <label>客户姓名</label>
                                <span>${customer.name || '-'}</span>
                            </div>
                            <div class="detail-item">
                                <label>性别</label>
                                <span>${genderMap[customer.gender] || '未知'}</span>
                            </div>
                            <div class="detail-item">
                                <label>客户备注</label>
                                <span>${customer.remark || '-'}</span>
                            </div>
                            <div class="detail-item">
                                <label>客户类型</label>
                                <span>${customer.type === 1 ? '微信用户' : '企业微信用户'}</span>
                            </div>
                            <div class="detail-item">
                                <label>企业名称</label>
                                <span>${customer.corp_name || '-'}</span>
                            </div>
                            <div class="detail-item">
                                <label>职位</label>
                                <span>${customer.position || '-'}</span>
                            </div>
                            <div class="detail-item">
                                <label>备注企业</label>
                                <span>${customer.remark_corp_name || '-'}</span>
                            </div>
                            <div class="detail-item">
                                <label>备注手机</label>
                                <span>${customer.remark_mobiles ? JSON.parse(customer.remark_mobiles).join(', ') || '-' : '-'}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 跟进信息 -->
                    <div style="margin-bottom: 24px;">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--grey-800);">👤 跟进信息</h3>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                            <div class="detail-item">
                                <label>所属员工</label>
                                <span>${customer.owner_name || '-'}</span>
                            </div>
                            <div class="detail-item">
                                <label>添加时间</label>
                                <span>${addTime}</span>
                            </div>
                            <div class="detail-item">
                                <label>添加方式</label>
                                <span>${addWayMap[customer.add_way] || '未知'}</span>
                            </div>
                            <div class="detail-item">
                                <label>来源渠道</label>
                                <span>${customer.state || '-'}</span>
                            </div>
                            <div class="detail-item" style="grid-column: 1 / -1;">
                                <label>描述信息</label>
                                <span>${customer.description || '-'}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 标签信息 -->
                    <div style="margin-bottom: 24px;">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--grey-800);">🏷️ 客户标签</h3>
                        <div style="display: flex; flex-direction: column; gap: 12px;">
                            ${enterpriseTags.length > 0 ? `
                                <div>
                                    <label style="font-size: 13px; color: var(--grey-600); margin-bottom: 8px; display: block;">企业标签</label>
                                    <div class="tag-list">
                                        ${enterpriseTags.map(tag => `<span class="tag">${tag.tag_name}</span>`).join('')}
                                    </div>
                                </div>
                            ` : ''}
                            ${personalTags.length > 0 ? `
                                <div>
                                    <label style="font-size: 13px; color: var(--grey-600); margin-bottom: 8px; display: block;">个人标签</label>
                                    <div class="tag-list">
                                        ${personalTags.map(tag => `<span class="tag" style="background: var(--info-light); color: var(--info);">${tag.tag_name}</span>`).join('')}
                                    </div>
                                </div>
                            ` : ''}
                            ${ruleTags.length > 0 ? `
                                <div>
                                    <label style="font-size: 13px; color: var(--grey-600); margin-bottom: 8px; display: block;">规则组标签</label>
                                    <div class="tag-list">
                                        ${ruleTags.map(tag => `<span class="tag" style="background: var(--warning-light); color: var(--warning);">${tag.tag_name}</span>`).join('')}
                                    </div>
                                </div>
                            ` : ''}
                            ${enterpriseTags.length === 0 && personalTags.length === 0 && ruleTags.length === 0 ? '<span style="color: var(--grey-400);">暂无标签</span>' : ''}
                        </div>
                    </div>
                    
                    <!-- 系统信息 -->
                    <div>
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--grey-800);">⚙️ 系统信息</h3>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                            <div class="detail-item">
                                <label>客户ID</label>
                                <span style="font-size: 12px; font-family: monospace;">${customer.id}</span>
                            </div>
                            <div class="detail-item">
                                <label>UnionID</label>
                                <span style="font-size: 12px; font-family: monospace;">${customer.unionid || '-'}</span>
                            </div>
                            <div class="detail-item">
                                <label>创建时间</label>
                                <span>${createdAt}</span>
                            </div>
                            <div class="detail-item">
                                <label>更新时间</label>
                                <span>${updatedAt}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer" style="border-top: 1px solid #e5e7eb; padding-top: 16px; display: flex; justify-content: flex-end; gap: 12px;">
                    <button class="btn btn-outlined" onclick="closeCustomerDetail()">关闭</button>
                    <button class="btn btn-primary" onclick="editCustomerInfo('${customer.id}')">
                        <i class="fas fa-edit"></i> 编辑客户
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('[查看详情] 错误:', error);
        showToast('加载客户详情失败', 'error');
    }
}

// 关闭客户详情
function closeCustomerDetail() {
    const modal = document.getElementById('customer-detail-modal');
    if (modal) {
        modal.remove();
    }
}

// 编辑客户信息（备注和标签）
async function editCustomerInfo(customerId) {
    try {
        showToast('正在加载客户信息...', 'info');
        
        // 关闭详情弹窗（如果打开）
        closeCustomerDetail();
        
        // 并行获取客户信息和标签库
        const [customerRes, tagsRes] = await Promise.all([
            fetch(`/api/customers/${customerId}?api_token=${apiToken}`),
            fetch(`/api/tags?api_token=${apiToken}`)
        ]);
        
        const customerData = await customerRes.json();
        const tagsData = await tagsRes.json();
        
        if (!customerData.success) {
            showToast('获取客户信息失败', 'error');
            return;
        }
        
        const customer = customerData.data;
        
        // 解析企业标签
        let enterpriseTags = [];
        try {
            if (customer.enterprise_tags) {
                enterpriseTags = JSON.parse(customer.enterprise_tags);
            }
        } catch (e) {
            console.error('解析标签失败:', e);
        }
        
        // 获取标签库
        const allTags = tagsData.success ? tagsData.data : [];
        
        // 创建编辑弹窗
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.id = 'edit-customer-modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                    <h2>✏️ 编辑客户信息</h2>
                    <button class="modal-close" onclick="closeEditCustomer()">×</button>
                </div>
                <div class="modal-body" style="padding: 24px;">
                    <div class="form-group" style="margin-bottom: 20px;">
                        <label class="form-label">客户姓名</label>
                        <input type="text" class="form-control" value="${customer.name || ''}" disabled style="background: #f5f5f5;">
                    </div>
                    
                    <div class="form-group" style="margin-bottom: 20px;">
                        <label class="form-label">客户备注 *</label>
                        <input type="text" class="form-control" id="edit-remark" value="${customer.remark || ''}" placeholder="请输入客户备注">
                        <small style="color: var(--grey-500); font-size: 12px;">修改后将同步到企业微信</small>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">客户标签</label>
                        <div id="edit-tags-container" style="min-height: 100px; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px;">
                            ${allTags.length > 0 ? `
                                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                    ${allTags.map(group => `
                                        <div style="margin-bottom: 12px; width: 100%;">
                                            <div style="font-size: 13px; color: var(--grey-600); margin-bottom: 8px; font-weight: 600;">${group.group_name}</div>
                                            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                                ${group.tags.map(tag => {
                                                    const isSelected = enterpriseTags.some(t => t.tag_id === tag.tag_id);
                                                    return `
                                                        <label style="cursor: pointer; display: inline-flex; align-items: center; padding: 6px 12px; border: 1px solid #e5e7eb; border-radius: 6px; background: ${isSelected ? 'var(--primary-light)' : '#fff'}; color: ${isSelected ? '#fff' : 'var(--grey-700)'}; transition: all 0.2s;">
                                                            <input type="checkbox" class="tag-checkbox" data-tag-id="${tag.tag_id}" data-tag-name="${tag.tag_name}" data-group-name="${group.group_name}" ${isSelected ? 'checked' : ''} style="margin-right: 6px;">
                                                            ${tag.tag_name}
                                                        </label>
                                                    `;
                                                }).join('')}
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : '<p style="color: var(--grey-400); font-size: 14px; margin: 0;">暂无可用标签，请先在企业微信中创建标签</p>'}
                        </div>
                        <small style="color: var(--grey-500); font-size: 12px; margin-top: 8px; display: block;">选中的标签将同步到企业微信</small>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outlined" onclick="closeEditCustomer()">取消</button>
                    <button class="btn btn-primary" onclick="saveCustomerInfo('${customer.id}', '${customer.owner_userid}')">
                        <i class="fas fa-save"></i> 保存并同步
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 监听标签复选框变化
        document.querySelectorAll('.tag-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const label = this.parentElement;
                if (this.checked) {
                    label.style.background = 'var(--primary-light)';
                    label.style.color = '#fff';
                } else {
                    label.style.background = '#fff';
                    label.style.color = 'var(--grey-700)';
                }
            });
        });
        
    } catch (error) {
        console.error('[编辑客户] 错误:', error);
        showToast('加载客户信息失败', 'error');
    }
}

// 关闭编辑弹窗
function closeEditCustomer() {
    const modal = document.getElementById('edit-customer-modal');
    if (modal) {
        modal.remove();
    }
}

// 保存客户信息并同步到企业微信
async function saveCustomerInfo(customerId, ownerUserid) {
    try {
        const remark = document.getElementById('edit-remark').value;
        
        // 获取选中的标签
        const selectedTags = [];
        document.querySelectorAll('.tag-checkbox:checked').forEach(checkbox => {
            selectedTags.push({
                tag_id: checkbox.dataset.tagId,
                tag_name: checkbox.dataset.tagName,
                group_name: checkbox.dataset.groupName
            });
        });
        
        showToast('正在保存并同步到企业微信...', 'info');
        
        // 调用后端API同步到企业微信
        const res = await fetch(`/api/customers/${customerId}/update?api_token=${apiToken}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                remark: remark,
                owner_userid: ownerUserid,
                tags: selectedTags.map(t => t.tag_id)
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('✅ 保存成功并已同步到企业微信', 'success');
            closeEditCustomer();
            loadCustomers(); // 重新加载列表
        } else {
            showToast(`保存失败: ${data.message}`, 'error');
        }
        
    } catch (error) {
        console.error('[保存客户] 错误:', error);
        showToast('保存失败，请检查网络连接', 'error');
    }
}

// 客户管理
window.viewAvatarLarge = viewAvatarLarge;
window.closeAvatarViewer = closeAvatarViewer;
window.syncCustomers = syncCustomers;
window.stopSyncTask = stopSyncTask;
window.closeSyncProgressModal = closeSyncProgressModal;
window.addCustomer = addCustomer;
window.exportCustomers = exportCustomers;
window.exportToExcel = exportToExcel;
window.exportToWeComSpreadsheet = exportToWeComSpreadsheet;
window.filterCustomers = filterCustomers;
window.applyFilters = applyFilters;
window.resetFilters = resetFilters;
window.cancelSelection = cancelSelection;
window.viewCustomer = viewCustomer;
window.editCustomer = editCustomer;
window.showCustomerDetail = showCustomerDetail;
window.batchUpdateOwner = batchUpdateOwner;
window.batchUpdateTags = batchUpdateTags;
window.batchSendMessage = batchSendMessage;
// 新增详情和编辑相关函数
window.viewCustomerDetail = viewCustomerDetail;
window.closeCustomerDetail = closeCustomerDetail;
window.editCustomerInfo = editCustomerInfo;
window.closeEditCustomer = closeEditCustomer;
window.saveCustomerInfo = saveCustomerInfo;

// 筛选器 - 标签和省份选择
window.showTagSelector = showTagSelector;
window.closeTagSelector = closeTagSelector;
window.confirmTagSelection = confirmTagSelection;
window.searchTags = searchTags;
window.showProvinceSelector = showProvinceSelector;
window.closeProvinceSelector = closeProvinceSelector;
window.confirmProvinceSelection = confirmProvinceSelection;
window.searchProvinces = searchProvinces;

// 企业标签
window.syncEnterpriseTags = syncEnterpriseTags;
window.loadEnterpriseTagsList = loadEnterpriseTagsList;
window.addTagGroup = addTagGroup;
window.editTagGroup = editTagGroup;
window.deleteTagGroup = deleteTagGroup;
window.addTagToGroup = addTagToGroup;
window.editTag = editTag;

// 通讯录
window.syncEmployees = syncEmployees;
window.exportEmployees = exportEmployees;
window.searchEmployees = searchEmployees;
window.filterEmployees = filterEmployees;
window.viewEmployee = viewEmployee;

// 智能表格 - 上传Excel
window.showUploadExcelDialog = showUploadExcelDialog;
window.closeUploadExcelDialog = closeUploadExcelDialog;
window.handleFileSelect = handleFileSelect;
window.createSpreadsheetFromExcel = createSpreadsheetFromExcel;

// 智能表格 - 表格操作
window.closeSpreadsheetDetail = closeSpreadsheetDetail;
window.syncSpreadsheet = syncSpreadsheet;
window.syncSpreadsheetById = syncSpreadsheetById;
window.openInWecom = openInWecom;
window.deleteSpreadsheet = deleteSpreadsheet;

// ========== 标签选择器功能 ==========
async function showTagSelector() {
    try {
        const res = await fetch(`/api/tags?api_token=${apiToken}`);
        const data = await res.json();
        
        if (data.success) {
            allTagGroups = data.data;
            renderTagGroups(allTagGroups);
            document.getElementById('tag-selector-modal').style.display = 'flex';
        }
    } catch (error) {
        console.error('[标签选择器] 加载失败', error);
        showToast('加载标签失败', 'error');
    }
}

function renderTagGroups(tagGroups) {
    const container = document.getElementById('tag-groups-list');
    
    if (!tagGroups || tagGroups.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--grey-500);">
                <i class="fas fa-tags" style="font-size: 48px; opacity: 0.3; margin-bottom: 12px;"></i>
                <p>暂无标签数据</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = tagGroups.map(group => `
        <div class="tag-group-item">
            <div class="tag-group-title">
                <i class="fas fa-folder"></i>
                ${group.group_name}
            </div>
            <div class="tag-list">
                ${group.tags.map(tag => `
                    <label class="tag-checkbox-item ${selectedTags.includes(tag.tag_id) ? 'selected' : ''}" data-tag-id="${tag.tag_id}">
                        <input type="checkbox" value="${tag.tag_id}" 
                               ${selectedTags.includes(tag.tag_id) ? 'checked' : ''}
                               onchange="toggleTagSelection('${tag.tag_id}', this)">
                        ${tag.tag_name}
                    </label>
                `).join('')}
            </div>
        </div>
    `).join('');
}

function toggleTagSelection(tagId, checkbox) {
    const label = checkbox.closest('.tag-checkbox-item');
    
    if (checkbox.checked) {
        if (!selectedTags.includes(tagId)) {
            selectedTags.push(tagId);
        }
        label.classList.add('selected');
    } else {
        selectedTags = selectedTags.filter(id => id !== tagId);
        label.classList.remove('selected');
    }
}

function searchTags() {
    const keyword = document.getElementById('tag-search').value.toLowerCase();
    
    if (!keyword) {
        renderTagGroups(allTagGroups);
        return;
    }
    
    const filtered = allTagGroups.map(group => {
        const matchedTags = group.tags.filter(tag => 
            tag.tag_name.toLowerCase().includes(keyword)
        );
        
        if (matchedTags.length > 0) {
            return {
                ...group,
                tags: matchedTags
            };
        }
        return null;
    }).filter(g => g !== null);
    
    renderTagGroups(filtered);
}

function confirmTagSelection() {
    console.log('[标签选择] 确认选择的标签:', selectedTags);
    const display = document.getElementById('selected-tags-display');
    
    if (selectedTags.length > 0) {
        // 显示已选标签数量
        display.textContent = `已选 ${selectedTags.length} 个标签`;
    } else {
        display.textContent = '企业标签';
    }
    
    closeTagSelector();
    applyFilters();
}

function closeTagSelector() {
    document.getElementById('tag-selector-modal').style.display = 'none';
}

// ========== 省份选择器功能 ==========
const provinces = [
    '北京', '天津', '河北', '山西', '内蒙古',
    '辽宁', '吉林', '黑龙江',
    '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东',
    '河南', '湖北', '湖南', '广东', '广西', '海南',
    '重庆', '四川', '贵州', '云南', '西藏',
    '陕西', '甘肃', '青海', '宁夏', '新疆',
    '香港', '澳门', '台湾'
];

function showProvinceSelector() {
    renderProvinces(provinces);
    document.getElementById('province-selector-modal').style.display = 'flex';
}

function renderProvinces(provinceList) {
    const container = document.getElementById('provinces-list');
    
    container.innerHTML = `
        <div class="province-list">
            ${provinceList.map(province => `
                <label class="province-item ${selectedProvinces.includes(province) ? 'selected' : ''}" data-province="${province}">
                    <input type="checkbox" value="${province}"
                           ${selectedProvinces.includes(province) ? 'checked' : ''}
                           onchange="toggleProvinceSelection('${province}', this)">
                    ${province}
                </label>
            `).join('')}
        </div>
    `;
}

function toggleProvinceSelection(province, checkbox) {
    const label = checkbox.closest('.province-item');
    
    if (checkbox.checked) {
        if (!selectedProvinces.includes(province)) {
            selectedProvinces.push(province);
        }
        label.classList.add('selected');
    } else {
        selectedProvinces = selectedProvinces.filter(p => p !== province);
        label.classList.remove('selected');
    }
}

function searchProvinces() {
    const keyword = document.getElementById('province-search').value.toLowerCase();
    
    const filtered = provinces.filter(p => p.toLowerCase().includes(keyword));
    renderProvinces(filtered);
}

function confirmProvinceSelection() {
    const display = document.getElementById('selected-province-display');
    
    if (selectedProvinces.length > 0) {
        display.textContent = `已选 ${selectedProvinces.length} 个省份`;
    } else {
        display.textContent = '省份';
    }
    
    closeProvinceSelector();
    applyFilters();
}

function closeProvinceSelector() {
    document.getElementById('province-selector-modal').style.display = 'none';
}
window.openSpreadsheetInWecom = openSpreadsheetInWecom;
window.showSpreadsheetDetailModal = showSpreadsheetDetailModal;

// 智能表格 - 手工创建
window.showCreateTableDialog = showCreateTableDialog;
window.closeCreateTableDialog = closeCreateTableDialog;
window.showTemplateSelector = showTemplateSelector;
window.closeTemplateSelector = closeTemplateSelector;
window.showAddFieldDialog = showAddFieldDialog;
window.closeAddFieldDialog = closeAddFieldDialog;
window.addFieldToList = addFieldToList;

// 配置
window.showConfig = showConfig;
window.saveConfig = saveConfig;
window.closeConfig = closeConfig;

// 优化提示
window.closeOptimizationModal = closeOptimizationModal;
window.openSmartsheetAndClose = openSmartsheetAndClose;

// ==================== 客户群列表功能 ====================

// 客户群列表状态
let groupsData = [];
let filteredGroups = [];
let currentGroupPage = 1;
let totalGroupPages = 1;
let totalGroupCount = 0;
let groupPageLimit = 20;

// 加载客户群列表
async function loadCustomerGroups() {
    console.log('[加载客户群列表]');
    const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
    
    try {
        const params = new URLSearchParams({
            api_token: apiToken,
            page: currentGroupPage,
            limit: groupPageLimit
        });
        
        // 添加筛选条件
        const search = document.getElementById('group-filter-search')?.value;
        const owner = document.getElementById('group-filter-owner')?.value;
        const type = document.getElementById('group-filter-type')?.value;
        const dateStart = document.getElementById('group-filter-date-start')?.value;
        const dateEnd = document.getElementById('group-filter-date-end')?.value;
        const tag = document.getElementById('group-filter-tag')?.value;
        
        if (search) params.append('search', search);
        if (owner) params.append('owner_userid', owner);
        if (type) params.append('group_type', type);
        if (dateStart) params.append('date_start', dateStart);
        if (dateEnd) params.append('date_end', dateEnd);
        if (tag) params.append('tag_id', tag);
        
        console.log('[请求参数]', params.toString());
        
        const response = await fetch(`/api/customer-groups?${params}`);
        const data = await response.json();
        
        console.log('[客户群数据]', data);
        
        if (data.success) {
            groupsData = data.data || [];
            filteredGroups = groupsData;
            totalGroupCount = data.total || 0;
            totalGroupPages = Math.ceil(totalGroupCount / groupPageLimit);
            
            renderCustomerGroups();
            updateGroupPagination();
            updateGroupResultCount();
        } else {
            showToast('加载客户群列表失败', 'error');
        }
    } catch (error) {
        console.error('[加载客户群失败]', error);
        showToast('加载客户群列表失败', 'error');
    }
}

// 渲染客户群列表
function renderCustomerGroups() {
    const tbody = document.getElementById('customer-groups-list');
    
    if (!tbody) {
        console.error('[渲染客户群] 表格容器不存在');
        return;
    }
    
    if (filteredGroups.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="13" style="text-align: center; padding: 60px 20px;">
                    <div style="font-size: 48px; opacity: 0.3; margin-bottom: 16px;">📭</div>
                    <div style="color: var(--grey-600); font-size: 16px; margin-bottom: 8px;">暂无客户群数据</div>
                    <div style="color: var(--grey-500); font-size: 14px; margin-bottom: 20px;">
                        点击右上角"同步群聊"按钮从企业微信同步客户群数据
                    </div>
                    <button class="btn btn-primary" onclick="syncCustomerGroups()">
                        <i class="fas fa-sync"></i> 立即同步
                    </button>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = filteredGroups.map((group, index) => {
        const rowNumber = (currentGroupPage - 1) * groupPageLimit + index + 1;
        const groupType = group.group_type === 'external' ? '外部群' : '内部群';
        const groupTypeClass = group.group_type === 'external' ? 'badge-primary' : 'badge-secondary';
        
        // 群状态
        const statusMap = {0: '正常', 1: '离职待继承', 2: '离职继承中', 3: '离职继承完成'};
        const status = statusMap[group.status] || '正常';
        const statusClass = group.status === 0 ? 'badge-success' : 'badge-warning';
        
        const notice = group.notice ? (group.notice.length > 20 ? group.notice.substring(0, 20) + '...' : group.notice) : '-';
        const createTime = group.create_time ? new Date(group.create_time * 1000).toLocaleString('zh-CN') : '-';
        
        // 渲染群标签
        const groupTags = group.tags || [];
        const tagsHtml = groupTags.length > 0 
            ? groupTags.map(tag => `<span class="badge badge-info" style="margin: 2px;">${tag.tag_name}</span>`).join('')
            : '<span style="color: var(--grey-400); font-size: 13px;">暂无标签</span>';
        
        return `
            <tr>
                <td>
                    <input type="checkbox" class="group-checkbox" value="${group.chat_id}" onchange="updateBatchTagButton()">
                </td>
                <td>${rowNumber}</td>
                <td>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 40px; height: 40px; background: var(--gradient-primary); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">
                            <i class="fas fa-users"></i>
                        </div>
                        <div>
                            <div style="font-weight: 600; color: var(--grey-800);">${group.name || '未命名群聊'}</div>
                            <div style="font-size: 12px; color: var(--grey-500);">ID: ${group.chat_id || '-'}</div>
                        </div>
                    </div>
                </td>
                <td>
                    <div style="font-weight: 500; color: var(--grey-800);">${group.owner_name || '-'}</div>
                    <div style="font-size: 12px; color: var(--grey-500);">${group.owner_userid || '-'}</div>
                </td>
                <td style="text-align: center;">
                    <span style="font-weight: 600; color: var(--grey-800); font-size: 16px;">${group.member_count || 0}</span>
                </td>
                <td style="text-align: center;">
                    <span style="font-weight: 600; color: var(--primary-main); font-size: 16px;">${group.external_member_count || 0}</span>
                </td>
                <td style="text-align: center;">
                    <span style="font-weight: 600; color: var(--secondary-main); font-size: 16px;">${group.internal_member_count || 0}</span>
                </td>
                <td>
                    <div style="max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${group.notice || ''}">
                        ${notice}
                    </div>
                </td>
                <td>
                    <span class="badge ${groupTypeClass}">${groupType}</span>
                </td>
                <td>
                    <span class="badge ${statusClass}">${status}</span>
                </td>
                <td>
                    <div style="display: flex; flex-wrap: wrap; gap: 4px; max-width: 200px;">
                        ${tagsHtml}
                    </div>
                </td>
                <td style="color: var(--grey-600); font-size: 13px;">${createTime}</td>
                <td>
                    <button class="btn btn-text btn-sm" onclick="showGroupTagDialog('${group.chat_id}')">
                        <i class="fas fa-tag"></i> 打标签
                    </button>
                    <button class="btn btn-text btn-sm" onclick="viewGroupDetail('${group.chat_id}')">
                        <i class="fas fa-eye"></i> 查看
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// 更新分页信息
function updateGroupPagination() {
    document.getElementById('group-current-page').textContent = currentGroupPage;
    document.getElementById('group-total-pages').textContent = totalGroupPages;
    document.getElementById('group-total-count').textContent = totalGroupCount;
}

// 更新筛选结果数量
function updateGroupResultCount() {
    const resultCount = document.getElementById('group-filter-result-count');
    if (resultCount && totalGroupCount > 0) {
        resultCount.innerHTML = `找到 <strong>${totalGroupCount}</strong> 个群聊`;
    } else if (resultCount) {
        resultCount.innerHTML = '';
    }
}

// 切换页码
function changeGroupPage(delta) {
    const newPage = currentGroupPage + delta;
    if (newPage >= 1 && newPage <= totalGroupPages) {
        currentGroupPage = newPage;
        loadCustomerGroups();
    }
}

// 筛选群聊
function filterGroups() {
    applyGroupFilters();
}

function applyGroupFilters() {
    currentGroupPage = 1;
    loadCustomerGroups();
}

// 重置筛选
function resetGroupFilters() {
    document.getElementById('group-filter-search').value = '';
    document.getElementById('group-filter-owner').value = '';
    document.getElementById('group-filter-type').value = '';
    document.getElementById('group-filter-date-start').value = '';
    document.getElementById('group-filter-date-end').value = '';
    document.getElementById('group-filter-tag').value = '';
    
    applyGroupFilters();
}

// ========== 客户群标签功能 ==========

// 加载标签列表到筛选器
async function loadTagsToFilter() {
    const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
    
    try {
        const response = await fetch(`/api/group-tags?api_token=${apiToken}`);
        const data = await response.json();
        
        if (data.success) {
            const tags = data.data || [];
            const select = document.getElementById('group-filter-tag');
            
            if (!select) return;
            
            // 保存当前选中值
            const currentValue = select.value;
            
            // 清空并重新填充选项
            select.innerHTML = '<option value="">群标签</option>';
            
            tags.forEach(group => {
                if (group.tag && group.tag.length > 0) {
                    const optgroup = document.createElement('optgroup');
                    optgroup.label = group.group_name;
                    
                    group.tag.forEach(tag => {
                        const option = document.createElement('option');
                        option.value = tag.id;
                        option.textContent = tag.name;
                        optgroup.appendChild(option);
                    });
                    
                    select.appendChild(optgroup);
                }
            });
            
            // 恢复之前的选中值
            if (currentValue) {
                select.value = currentValue;
            }
        }
    } catch (error) {
        console.error('[加载标签列表] 错误:', error);
    }
}

// 全选/取消全选
function toggleSelectAllGroups() {
    const selectAll = document.getElementById('select-all-groups');
    const checkboxes = document.querySelectorAll('.group-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
    });
    
    updateBatchTagButton();
}

// 更新批量打标签按钮显示状态
function updateBatchTagButton() {
    const checkboxes = document.querySelectorAll('.group-checkbox:checked');
    const batchBtn = document.getElementById('batch-tag-btn');
    
    if (checkboxes.length > 0) {
        batchBtn.style.display = 'inline-flex';
        batchBtn.innerHTML = `<i class="fas fa-tags"></i> 批量打标签 (${checkboxes.length})`;
    } else {
        batchBtn.style.display = 'none';
    }
}

// 显示单个打标签对话框
function showGroupTagDialog(chatId) {
    window.currentTaggingGroupId = chatId;
    window.isBatchTagging = false;
    
    // 加载标签列表
    loadTagsForDialog();
    
    // 显示对话框
    const dialog = document.getElementById('group-tag-dialog');
    if (dialog) {
        dialog.style.display = 'flex';
    }
}

// 显示批量打标签对话框
function showBatchTagDialog() {
    const checkboxes = document.querySelectorAll('.group-checkbox:checked');
    
    if (checkboxes.length === 0) {
        showToast('请先选择要打标签的群聊', 'warning');
        return;
    }
    
    window.currentTaggingGroupIds = Array.from(checkboxes).map(cb => cb.value);
    window.isBatchTagging = true;
    
    // 加载标签列表
    loadTagsForDialog();
    
    // 显示对话框
    const dialog = document.getElementById('group-tag-dialog');
    if (dialog) {
        dialog.style.display = 'flex';
    }
}

// 关闭打标签对话框
function closeGroupTagDialog() {
    const dialog = document.getElementById('group-tag-dialog');
    if (dialog) {
        dialog.style.display = 'none';
    }
    
    window.currentTaggingGroupId = null;
    window.currentTaggingGroupIds = null;
    window.isBatchTagging = false;
}

// 加载标签列表到对话框
async function loadTagsForDialog() {
    const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
    
    try {
        const response = await fetch(`/api/group-tags?api_token=${apiToken}`);
        const data = await response.json();
        
        if (data.success) {
            const tags = data.data || [];
            renderTagsInDialog(tags);
        } else {
            showToast('加载标签失败', 'error');
        }
    } catch (error) {
        console.error('[加载标签] 错误:', error);
        showToast('加载标签失败，请检查网络连接', 'error');
    }
}

// 在对话框中渲染标签
function renderTagsInDialog(tagGroups) {
    const container = document.getElementById('dialog-tags-container');
    
    if (!container) return;
    
    if (tagGroups.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--grey-500);">
                <i class="fas fa-tags" style="font-size: 48px; opacity: 0.3; margin-bottom: 16px;"></i>
                <div>暂无标签</div>
                <div style="font-size: 14px; margin-top: 8px;">请先到"客户群标签"菜单创建标签</div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = tagGroups.map(group => `
        <div class="tag-group-section" style="margin-bottom: 20px;">
            <h4 style="font-size: 14px; font-weight: 600; color: var(--grey-700); margin-bottom: 12px;">
                ${group.group_name}
            </h4>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                ${group.tag.map(tag => `
                    <label class="tag-checkbox-label">
                        <input type="checkbox" name="selected-tags" value="${tag.id}" data-tag-name="${tag.name}">
                        <span>${tag.name}</span>
                    </label>
                `).join('')}
            </div>
        </div>
    `).join('');
}

// 保存群标签
async function saveGroupTags() {
    const selectedTags = Array.from(document.querySelectorAll('input[name="selected-tags"]:checked'))
        .map(input => ({
            tag_id: input.value,
            tag_name: input.getAttribute('data-tag-name')
        }));
    
    if (selectedTags.length === 0) {
        showToast('请至少选择一个标签', 'warning');
        return;
    }
    
    const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
    
    try {
        let response;
        
        if (window.isBatchTagging) {
            // 批量打标签
            response = await fetch(`/api/group-tags/batch-assign?api_token=${apiToken}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    chat_ids: window.currentTaggingGroupIds,
                    tags: selectedTags
                })
            });
        } else {
            // 单个打标签
            response = await fetch(`/api/group-tags/assign?api_token=${apiToken}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    chat_id: window.currentTaggingGroupId,
                    tags: selectedTags
                })
            });
        }
        
        const data = await response.json();
        
        if (data.success) {
            showToast('打标签成功！', 'success');
            closeGroupTagDialog();
            
            // 刷新列表
            loadCustomerGroups();
            
            // 取消所有选中
            document.getElementById('select-all-groups').checked = false;
            updateBatchTagButton();
        } else {
            showToast(data.message || '打标签失败', 'error');
        }
    } catch (error) {
        console.error('[打标签] 错误:', error);
        showToast('打标签失败，请检查网络连接', 'error');
    }
}

// 同步客户群
let currentGroupSyncTaskId = null;
let groupSyncInterval = null;

async function syncCustomerGroups() {
    console.log('[同步客户群]');
    
    const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
    const wecom_config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
    
    console.log('[配置检查]', {
        has_corpid: !!wecom_config.corpid,
        has_customer_secret: !!wecom_config.customer_secret,
        has_app_secret: !!wecom_config.app_secret
    });
    
    try {
        // 启动同步任务
        const response = await fetch(`/api/sync/customer-groups?api_token=${apiToken}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ config: wecom_config })
        });
        
        const data = await response.json();
        console.log('[同步任务启动]', data);
        
        if (data.success && data.task_id) {
            currentGroupSyncTaskId = data.task_id;
            showGroupSyncProgress();
            startGroupSyncPolling();
        } else {
            showToast(data.message || '启动同步任务失败', 'error');
        }
    } catch (error) {
        console.error('[启动同步失败]', error);
        showToast('启动同步任务失败，请检查网络连接', 'error');
    }
}

function showGroupSyncProgress() {
    document.getElementById('group-sync-progress-modal').classList.add('show');
    document.getElementById('group-sync-cancel-btn').style.display = '';
    document.getElementById('group-sync-close-btn').style.display = 'none';
    document.getElementById('group-sync-error').style.display = 'none';
    
    // 重置显示
    document.getElementById('group-sync-status-text').textContent = '准备中...';
    document.getElementById('group-sync-progress-text').textContent = '0%';
    document.getElementById('group-sync-progress-bar').style.width = '0%';
    document.getElementById('group-sync-total').textContent = '0';
    document.getElementById('group-sync-processed').textContent = '0';
    document.getElementById('group-sync-added').textContent = '0';
    document.getElementById('group-sync-updated').textContent = '0';
}

function startGroupSyncPolling() {
    if (groupSyncInterval) {
        clearInterval(groupSyncInterval);
    }
    
    groupSyncInterval = setInterval(async () => {
        if (!currentGroupSyncTaskId) {
            clearInterval(groupSyncInterval);
            return;
        }
        
        try {
            const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
            const response = await fetch(`/api/sync/customer-groups/status/${currentGroupSyncTaskId}?api_token=${apiToken}`);
            const data = await response.json();
            
            if (data.success && data.data) {
                updateGroupSyncProgress(data.data);
                
                // 如果任务完成或失败，停止轮询
                if (data.data.status === 'completed' || data.data.status === 'failed') {
                    clearInterval(groupSyncInterval);
                    groupSyncInterval = null;
                    
                    if (data.data.status === 'completed') {
                        // 延迟加载列表，让用户看到完成状态
                        setTimeout(() => {
                            loadCustomerGroups();
                        }, 1000);
                    }
                }
            }
        } catch (error) {
            console.error('[获取同步状态失败]', error);
        }
    }, 1000); // 每秒更新一次
}

function updateGroupSyncProgress(status) {
    const progress = status.progress || 0;
    const statusText = status.status === 'running' ? '同步中...' : 
                      status.status === 'completed' ? '✅ 同步完成！' :
                      status.status === 'failed' ? '❌ 同步失败' : '准备中...';
    
    document.getElementById('group-sync-status-text').textContent = statusText;
    document.getElementById('group-sync-progress-text').textContent = progress + '%';
    document.getElementById('group-sync-progress-bar').style.width = progress + '%';
    document.getElementById('group-sync-total').textContent = status.total_count || 0;
    document.getElementById('group-sync-processed').textContent = status.processed_count || 0;
    document.getElementById('group-sync-added').textContent = status.added_count || 0;
    document.getElementById('group-sync-updated').textContent = status.updated_count || 0;
    
    // 如果完成或失败，显示关闭按钮
    if (status.status === 'completed' || status.status === 'failed') {
        document.getElementById('group-sync-cancel-btn').style.display = 'none';
        document.getElementById('group-sync-close-btn').style.display = '';
        
        if (status.status === 'failed' && status.error_message) {
            const errorDiv = document.getElementById('group-sync-error');
            errorDiv.textContent = '错误: ' + status.error_message;
            errorDiv.style.display = '';
        }
    }
}

async function cancelGroupSync() {
    if (!currentGroupSyncTaskId) return;
    
    if (!confirm('确定要取消同步吗？')) return;
    
    try {
        const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
        const response = await fetch(`/api/sync/customer-groups/cancel/${currentGroupSyncTaskId}?api_token=${apiToken}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            showToast('同步已取消', 'info');
            closeGroupSyncProgress();
        }
    } catch (error) {
        console.error('[取消同步失败]', error);
    }
}

function closeGroupSyncProgress() {
    document.getElementById('group-sync-progress-modal').classList.remove('show');
    if (groupSyncInterval) {
        clearInterval(groupSyncInterval);
        groupSyncInterval = null;
    }
    currentGroupSyncTaskId = null;
}

// 导出群聊
function exportGroups() {
    showToast('导出功能开发中...', 'info');
}

// 查看群聊详情
function viewGroupDetail(chatId) {
    showToast(`查看群聊详情功能开发中: ${chatId}`, 'info');
}

// 导出全局函数
window.loadCustomerGroups = loadCustomerGroups;
window.renderCustomerGroups = renderCustomerGroups;
window.changeGroupPage = changeGroupPage;
window.filterGroups = filterGroups;
window.applyGroupFilters = applyGroupFilters;
window.resetGroupFilters = resetGroupFilters;
window.syncCustomerGroups = syncCustomerGroups;
window.cancelGroupSync = cancelGroupSync;
window.closeGroupSyncProgress = closeGroupSyncProgress;
window.exportGroups = exportGroups;
window.viewGroupDetail = viewGroupDetail;

// 导出客户群标签相关函数
window.toggleSelectAllGroups = toggleSelectAllGroups;
window.updateBatchTagButton = updateBatchTagButton;
window.showGroupTagDialog = showGroupTagDialog;
window.showBatchTagDialog = showBatchTagDialog;
window.closeGroupTagDialog = closeGroupTagDialog;
window.loadTagsForDialog = loadTagsForDialog;
window.saveGroupTags = saveGroupTags;
window.loadTagsToFilter = loadTagsToFilter;

// ==================== 系统设置功能 ====================

// 配置历史记录
let configHistory = JSON.parse(localStorage.getItem('config_history') || '[]');

// 加载企业微信配置
function loadWecomConfig() {
    const config = JSON.parse(localStorage.getItem('wecom_config') || '{}');
    
    document.getElementById('settings-corpid').value = config.corpid || '';
    document.getElementById('settings-app-secret').value = config.app_secret || '';
    document.getElementById('settings-agentid').value = config.agentid || '';
    document.getElementById('settings-contact-secret').value = config.contact_secret || '';
    document.getElementById('settings-customer-secret').value = config.customer_secret || '';
    
    renderConfigHistory();
}

// 保存企业微信配置
function saveWecomConfig() {
    const config = {
        corpid: document.getElementById('settings-corpid').value.trim(),
        app_secret: document.getElementById('settings-app-secret').value.trim(),
        agentid: document.getElementById('settings-agentid').value.trim(),
        contact_secret: document.getElementById('settings-contact-secret').value.trim(),
        customer_secret: document.getElementById('settings-customer-secret').value.trim()
    };
    
    // 验证必填项
    if (!config.corpid) {
        showToast('请填写企业 ID', 'error');
        return;
    }
    if (!config.app_secret) {
        showToast('请填写自建应用 Secret', 'error');
        return;
    }
    if (!config.agentid) {
        showToast('请填写应用 AgentId', 'error');
        return;
    }
    
    // 保存配置
    localStorage.setItem('wecom_config', JSON.stringify(config));
    
    // 记录历史
    const historyItem = {
        id: Date.now(),
        type: '企业微信配置',
        content: `企业ID: ${config.corpid.substring(0, 10)}***, AgentId: ${config.agentid}`,
        timestamp: new Date().toLocaleString('zh-CN'),
        operator: '系统管理员'
    };
    
    configHistory.unshift(historyItem);
    if (configHistory.length > 50) {
        configHistory = configHistory.slice(0, 50); // 只保留最近50条
    }
    localStorage.setItem('config_history', JSON.stringify(configHistory));
    
    showToast('配置保存成功！', 'success');
    renderConfigHistory();
}

// 重置企业微信配置
function resetWecomConfig() {
    if (!confirm('确定要重置企业微信配置吗？')) {
        return;
    }
    
    document.getElementById('settings-corpid').value = '';
    document.getElementById('settings-app-secret').value = '';
    document.getElementById('settings-agentid').value = '';
    document.getElementById('settings-contact-secret').value = '';
    document.getElementById('settings-customer-secret').value = '';
    
    showToast('配置已重置', 'info');
}

// 渲染配置历史记录
function renderConfigHistory() {
    const tbody = document.getElementById('config-history-list');
    
    if (configHistory.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 60px 20px; color: var(--grey-500);">
                    <i class="fas fa-history" style="font-size: 48px; margin-bottom: 16px; display: block; opacity: 0.3;"></i>
                    <p style="font-size: 16px;">暂无配置历史记录</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = configHistory.map((item, index) => `
        <tr>
            <td>${index + 1}</td>
            <td><span class="badge badge-primary">${item.type}</span></td>
            <td style="color: var(--grey-700);">${item.content}</td>
            <td style="color: var(--grey-600); font-size: 13px;">${item.timestamp}</td>
            <td style="color: var(--grey-600);">${item.operator}</td>
            <td>
                <button class="btn-action btn-view" onclick="viewConfigDetail('${item.id}')">
                    <i class="fas fa-eye"></i> 查看
                </button>
            </td>
        </tr>
    `).join('');
}

// 查看配置详情
function viewConfigDetail(id) {
    const item = configHistory.find(h => h.id == id);
    if (!item) {
        showToast('配置记录不存在', 'error');
        return;
    }
    
    alert(`配置类型: ${item.type}\n配置内容: ${item.content}\n保存时间: ${item.timestamp}\n操作人: ${item.operator}`);
}

// 导出配置
window.saveWecomConfig = saveWecomConfig;
window.resetWecomConfig = resetWecomConfig;
window.viewConfigDetail = viewConfigDetail;

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否在系统设置模块
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('module') === 'settings') {
        loadWecomConfig();
    }
});

