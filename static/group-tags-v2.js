// ========== 客户群标签模块 ==========
console.log('[客户群标签] 脚本开始执行...', new Date().toISOString());

// 全局变量
if (typeof window.groupTagsList === 'undefined') {
    window.groupTagsList = [];
}
if (typeof window.currentEditingGroupId === 'undefined') {
    window.currentEditingGroupId = null;
}
if (typeof window.currentEditingTagId === 'undefined') {
    window.currentEditingTagId = null;
}

// apiToken 已在 script.js 中定义，这里不需要重复声明
console.log('[客户群标签] 使用全局 apiToken:', typeof apiToken !== 'undefined' ? 'OK' : 'Missing');

// 加载客户群标签列表
async function loadGroupTags() {
    try {
        console.log('[客户群标签] 开始加载...');
        
        const res = await fetch(`/api/group-tags?api_token=${apiToken}`);
        const data = await res.json();
        
        if (data.success) {
            window.window.groupTagsList = data.data || [];
            renderGroupTags(window.window.groupTagsList);
            console.log('[客户群标签] 加载成功', window.window.groupTagsList.length);
        } else {
            showToast(data.message || '加载失败', 'error');
        }
    } catch (error) {
        console.error('[客户群标签] 加载失败', error);
        showToast('加载失败，请检查网络连接', 'error');
    }
}

// 渲染标签组列表
function renderGroupTags(tags) {
    const container = document.getElementById('group-tags-container');
    const emptyState = document.getElementById('group-tags-empty');
    
    if (!tags || tags.length === 0) {
        container.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    
    container.innerHTML = tags.map(group => `
        <div class="group-tag-card" data-group-id="${group.group_id}">
            <div class="group-tag-header">
                <div class="group-tag-title">
                    <h3>${escapeHtml(group.group_name)}</h3>
                    <span class="group-tag-count">${group.tag.length} 个标签</span>
                </div>
                <div class="group-tag-actions">
                    <button class="btn btn-outlined btn-sm" onclick="editGroupTag('${group.group_id}')">
                        <i class="fas fa-edit"></i> 编辑
                    </button>
                    <button class="btn btn-outlined btn-sm" onclick="deleteGroupTag('${group.group_id}', '${escapeHtml(group.group_name)}')">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                </div>
            </div>
            <div class="tag-list-container">
                ${group.tag.length > 0 ? group.tag.map(tag => `
                    <div class="tag-item" data-tag-id="${tag.id}">
                        <span class="tag-item-name">${escapeHtml(tag.name)}</span>
                        <span class="tag-group-count">${tag.group_count || 0} 个群</span>
                        <div class="tag-item-actions">
                            <button class="tag-item-btn" onclick="editSingleTag('${tag.id}', '${group.group_id}')" title="编辑">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="tag-item-btn delete-btn" onclick="deleteSingleTag('${tag.id}', '${escapeHtml(tag.name)}')" title="删除">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                `).join('') : '<div class="empty-tag-group"><i class="fas fa-tags"></i><p>该标签组暂无标签</p></div>'}
            </div>
        </div>
    `).join('');
}

// 搜索标签
function searchGroupTags() {
    const keyword = document.getElementById('group-tag-search').value.trim().toLowerCase();
    
    if (!keyword) {
        renderGroupTags(window.groupTagsList);
        return;
    }
    
    const filtered = window.groupTagsList.filter(group => {
        // 搜索标签组名称
        if (group.group_name.toLowerCase().includes(keyword)) {
            return true;
        }
        // 搜索标签名称
        return group.tag.some(tag => tag.name.toLowerCase().includes(keyword));
    }).map(group => {
        // 如果是标签匹配，只显示匹配的标签
        if (!group.group_name.toLowerCase().includes(keyword)) {
            return {
                ...group,
                tag: group.tag.filter(tag => tag.name.toLowerCase().includes(keyword))
            };
        }
        return group;
    });
    
    renderGroupTags(filtered);
}

// 同步标签
async function syncGroupTags() {
    try {
        showToast('正在检查标签数据...', 'info');
        
        const res = await fetch(`/api/sync/group-tags?api_token=${apiToken}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({})
        });
        
        const data = await res.json();
        
        if (data.success && data.task_id) {
            // 显示进度弹窗
            showGroupTagsSyncModal(data.task_id);
        } else if (data.success) {
            showToast('检查完成！', 'success');
            loadGroupTags(); // 重新加载列表
        } else {
            showToast(data.message || '检查失败', 'error');
        }
    } catch (error) {
        console.error('[客户群标签] 检查失败', error);
        showToast('检查失败，请检查网络连接', 'error');
    }
}

// 显示新建标签组对话框
function showAddGroupTagDialog() {
    window.currentEditingGroupId = null;
    document.getElementById('group-tag-edit-dialog-title').textContent = '新建标签组';
    document.getElementById('group-tag-group-id').value = '';
    document.getElementById('group-tag-group-name').value = '';
    document.getElementById('group-tag-order').value = '1';
    
    // 清空并添加一个空的标签输入框
    const container = document.getElementById('group-tag-tags-container');
    container.innerHTML = '';
    addTagInput();
    
    document.getElementById('group-tag-edit-dialog').style.display = 'flex';
}

// 编辑标签组
function editGroupTag(groupId) {
    const group = window.groupTagsList.find(g => g.group_id === groupId);
    if (!group) return;
    
    window.currentEditingGroupId = groupId;
    document.getElementById('group-tag-edit-dialog-title').textContent = '编辑标签组';
    document.getElementById('group-tag-group-id').value = groupId;
    document.getElementById('group-tag-group-name').value = group.group_name;
    document.getElementById('group-tag-order').value = group.order || 1;
    
    // 填充已有标签
    const container = document.getElementById('group-tag-tags-container');
    container.innerHTML = '';
    
    if (group.tag && group.tag.length > 0) {
        group.tag.forEach(tag => {
            addTagInput(tag.name, tag.id, tag.order || 1);
        });
    } else {
        addTagInput();
    }
    
    document.getElementById('group-tag-edit-dialog').style.display = 'flex';
}

// 添加标签输入框
function addTagInput(name = '', tagId = '', order = 1) {
    const container = document.getElementById('group-tag-tags-container');
    const index = container.children.length;
    
    const div = document.createElement('div');
    div.className = 'tag-input-item';
    div.innerHTML = `
        <input type="text" class="form-control" placeholder="标签名称" value="${escapeHtml(name)}" data-tag-id="${tagId}" data-order="${order}">
        <input type="number" class="form-control" placeholder="排序" value="${order}" style="width: 100px;" min="0">
        <button type="button" class="btn btn-outlined btn-sm" onclick="this.parentElement.remove()">
            <i class="fas fa-trash"></i>
        </button>
    `;
    
    container.appendChild(div);
}

// 保存标签组
async function saveGroupTag() {
    const groupId = document.getElementById('group-tag-group-id').value;
    const groupName = document.getElementById('group-tag-group-name').value.trim();
    const order = parseInt(document.getElementById('group-tag-order').value) || 1;
    
    if (!groupName) {
        showToast('请输入标签组名称', 'error');
        return;
    }
    
    // 获取标签列表
    const tagInputs = document.querySelectorAll('#group-tag-tags-container .tag-input-item');
    const tags = [];
    
    tagInputs.forEach(item => {
        const nameInput = item.querySelector('input[type="text"]');
        const orderInput = item.querySelector('input[type="number"]');
        const name = nameInput.value.trim();
        const tagId = nameInput.dataset.tagId;
        const tagOrder = parseInt(orderInput.value) || 1;
        
        if (name) {
            const tag = {
                name: name,
                order: tagOrder
            };
            if (tagId) {
                tag.id = tagId;
            }
            tags.push(tag);
        }
    });
    
    if (tags.length === 0) {
        showToast('请至少添加一个标签', 'error');
        return;
    }
    
    try {
        const url = groupId 
            ? `/api/group-tags/${groupId}?api_token=${apiToken}`
            : `/api/group-tags?api_token=${apiToken}`;
        
        const method = groupId ? 'PUT' : 'POST';
        
        const res = await fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                group_id: groupId || undefined,
                group_name: groupName,
                order: order,
                tag: tags
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast(groupId ? '更新成功' : '创建成功', 'success');
            closeGroupTagEditDialog();
            loadGroupTags();
        } else {
            showToast(data.message || '保存失败', 'error');
        }
    } catch (error) {
        console.error('[客户群标签] 保存失败', error);
        showToast('保存失败，请检查网络连接', 'error');
    }
}

// 关闭标签组对话框
function closeGroupTagDialog() {
    document.getElementById('group-tag-dialog').style.display = 'none';
    window.currentEditingGroupId = null;
}

// 关闭新建/编辑标签组对话框
function closeGroupTagEditDialog() {
    document.getElementById('group-tag-edit-dialog').style.display = 'none';
    window.currentEditingGroupId = null;
}

// 删除标签组
async function deleteGroupTag(groupId, groupName) {
    if (!confirm(`确定要删除标签组"${groupName}"吗？\n\n删除后，该标签组下的所有标签也将被删除。`)) {
        return;
    }
    
    try {
        const res = await fetch(`/api/group-tags/${groupId}?api_token=${apiToken}`, {
            method: 'DELETE'
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('删除成功', 'success');
            loadGroupTags();
        } else {
            showToast(data.message || '删除失败', 'error');
        }
    } catch (error) {
        console.error('[客户群标签] 删除失败', error);
        showToast('删除失败，请检查网络连接', 'error');
    }
}

// 编辑单个标签
function editSingleTag(tagId, groupId) {
    const group = window.groupTagsList.find(g => g.group_id === groupId);
    if (!group) return;
    
    const tag = group.tag.find(t => t.id === tagId);
    if (!tag) return;
    
    window.currentEditingTagId = tagId;
    window.currentEditingGroupId = groupId;
    
    document.getElementById('edit-tag-id').value = tagId;
    document.getElementById('edit-tag-group-id').value = groupId;
    document.getElementById('edit-tag-name').value = tag.name;
    document.getElementById('edit-tag-order').value = tag.order || 1;
    
    document.getElementById('edit-tag-dialog').style.display = 'flex';
}

// 保存编辑的标签
async function saveEditTag() {
    const tagId = document.getElementById('edit-tag-id').value;
    const groupId = document.getElementById('edit-tag-group-id').value;
    const name = document.getElementById('edit-tag-name').value.trim();
    const order = parseInt(document.getElementById('edit-tag-order').value) || 1;
    
    if (!name) {
        showToast('请输入标签名称', 'error');
        return;
    }
    
    try {
        const res = await fetch(`/api/group-tags/${groupId}/tags/${tagId}?api_token=${apiToken}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: name,
                order: order
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('更新成功', 'success');
            closeEditTagDialog();
            loadGroupTags();
        } else {
            showToast(data.message || '更新失败', 'error');
        }
    } catch (error) {
        console.error('[客户群标签] 更新失败', error);
        showToast('更新失败，请检查网络连接', 'error');
    }
}

// 关闭编辑标签对话框
function closeEditTagDialog() {
    document.getElementById('edit-tag-dialog').style.display = 'none';
    window.currentEditingTagId = null;
    window.currentEditingGroupId = null;
}

// 删除单个标签
async function deleteSingleTag(tagId, tagName) {
    if (!confirm(`确定要删除标签"${tagName}"吗？`)) {
        return;
    }
    
    // 找到标签所属的组
    let groupId = null;
    for (const group of window.groupTagsList) {
        if (group.tag.some(t => t.id === tagId)) {
            groupId = group.group_id;
            break;
        }
    }
    
    if (!groupId) {
        showToast('找不到标签所属的组', 'error');
        return;
    }
    
    try {
        const res = await fetch(`/api/group-tags/${groupId}/tags/${tagId}?api_token=${apiToken}`, {
            method: 'DELETE'
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('删除成功', 'success');
            loadGroupTags();
        } else {
            showToast(data.message || '删除失败', 'error');
        }
    } catch (error) {
        console.error('[客户群标签] 删除失败', error);
        showToast('删除失败，请检查网络连接', 'error');
    }
}

// HTML 转义函数
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

// ========== 同步进度弹窗 ==========
let currentGroupTagsSyncTaskId = null;
let groupTagsSyncPollInterval = null;

function showGroupTagsSyncModal(taskId) {
    currentGroupTagsSyncTaskId = taskId;
    
    // 创建进度对话框
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.id = 'group-tags-sync-modal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h2>📊 正在检查标签数据</h2>
                <button class="modal-close" onclick="closeGroupTagsSyncModal()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #666;">×</button>
            </div>
            <div class="modal-body">
                <div style="padding: 20px;">
                    <!-- 进度条 -->
                    <div style="margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span id="group-tags-sync-text">准备中...</span>
                            <span id="group-tags-sync-percent">0%</span>
                        </div>
                        <div style="background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div id="group-tags-sync-bar" style="background: linear-gradient(90deg, #ff6b1a, #ff8d4d); height: 100%; width: 0%; transition: width 0.3s;"></div>
                        </div>
                    </div>
                    
                    <!-- 提示信息 -->
                    <div style="margin-top: 20px; padding: 16px; background: #eff6ff; border-left: 3px solid #2196F3; border-radius: 4px;">
                        <p style="margin: 0; font-size: 14px; color: #1565C0; line-height: 1.6;">
                            💡 <strong>提示：</strong>本系统使用自建标签系统，标签完全由您自主创建和管理。<br>
                            如需创建新标签，请点击「新建标签组」按钮。
                        </p>
                    </div>
                    
                    <!-- 统计信息 -->
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px;">
                        <div style="text-align: center; padding: 15px; background: #f9fafb; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: 600; color: #6b7280;" id="group-tags-sync-total">0</div>
                            <div style="font-size: 12px; color: #9ca3af; margin-top: 4px;">标签组</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f0fdf4; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: 600; color: #10b981;" id="group-tags-sync-added">-</div>
                            <div style="font-size: 12px; color: #6ee7b7; margin-top: 4px;">-</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #eff6ff; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: 600; color: #3b82f6;" id="group-tags-sync-updated">-</div>
                            <div style="font-size: 12px; color: #93c5fd; margin-top: 4px;">-</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #fef2f2; border-radius: 8px;">
                            <div style="font-size: 24px; font-weight: 600; color: #ef4444;" id="group-tags-sync-failed">-</div>
                            <div style="font-size: 12px; color: #fca5a5; margin-top: 4px;">-</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    // 开始轮询任务状态
    pollGroupTagsSyncProgress(taskId);
}

function closeGroupTagsSyncModal() {
    if (groupTagsSyncPollInterval) {
        clearInterval(groupTagsSyncPollInterval);
        groupTagsSyncPollInterval = null;
    }
    
    const modal = document.getElementById('group-tags-sync-modal');
    if (modal) {
        modal.remove();
    }
    
    currentGroupTagsSyncTaskId = null;
    
    // 重新加载标签列表
    loadGroupTags();
}

async function pollGroupTagsSyncProgress(taskId) {
    // 清除之前的轮询
    if (groupTagsSyncPollInterval) {
        clearInterval(groupTagsSyncPollInterval);
    }
    
    // 每秒轮询一次
    groupTagsSyncPollInterval = setInterval(async () => {
        try {
            const res = await fetch(`/api/sync/group-tags/status/${taskId}?api_token=${apiToken}`);
            const result = await res.json();
            
            if (result.success && result.data) {
                const data = result.data;
                
                // 更新进度条
                document.getElementById('group-tags-sync-bar').style.width = data.progress + '%';
                document.getElementById('group-tags-sync-percent').textContent = data.progress + '%';
                document.getElementById('group-tags-sync-text').textContent = data.message;
                
                // 更新统计
                document.getElementById('group-tags-sync-total').textContent = data.total || 0;
                document.getElementById('group-tags-sync-added').textContent = data.added || 0;
                document.getElementById('group-tags-sync-updated').textContent = data.updated || 0;
                document.getElementById('group-tags-sync-failed').textContent = data.failed || 0;
                
                // 任务完成或失败
                if (data.status === 'completed' || data.status === 'failed' || data.status === 'stopped') {
                    clearInterval(groupTagsSyncPollInterval);
                    groupTagsSyncPollInterval = null;
                    
                    if (data.status === 'completed') {
                        showToast('同步完成！', 'success');
                        setTimeout(() => {
                            closeGroupTagsSyncModal();
                        }, 2000);
                    } else if (data.status === 'failed') {
                        showToast('同步失败: ' + data.message, 'error');
                    } else if (data.status === 'stopped') {
                        showToast('同步已停止', 'warning');
                    }
                }
            }
        } catch (error) {
            console.error('[客户群标签] 轮询状态失败:', error);
        }
    }, 1000);
}

async function stopGroupTagsSyncTask() {
    if (!currentGroupTagsSyncTaskId) {
        showToast('没有正在运行的同步任务', 'warning');
        return;
    }
    
    if (!confirm('确定要停止同步吗？')) {
        return;
    }
    
    try {
        const res = await fetch(`/api/sync/group-tags/stop/${currentGroupTagsSyncTaskId}?api_token=${apiToken}`, {
            method: 'POST'
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('同步已停止', 'success');
            closeGroupTagsSyncModal();
        } else {
            showToast('停止失败', 'error');
        }
    } catch (error) {
        console.error('[客户群标签] 停止同步失败:', error);
        showToast('停止失败', 'error');
    }
}

// ========== 导出全局函数（确保 HTML 的 onclick 能访问）==========
window.loadGroupTags = loadGroupTags;
window.syncGroupTags = syncGroupTags;
window.showAddGroupTagDialog = showAddGroupTagDialog;
window.closeGroupTagDialog = closeGroupTagDialog;
window.closeGroupTagEditDialog = closeGroupTagEditDialog;
window.saveGroupTag = saveGroupTag;
window.editGroupTag = editGroupTag;
window.deleteGroupTag = deleteGroupTag;
window.saveEditTag = saveEditTag;
window.closeEditTagDialog = closeEditTagDialog;
window.deleteSingleTag = deleteSingleTag;
window.searchGroupTags = searchGroupTags;
window.closeGroupTagsSyncModal = closeGroupTagsSyncModal;
window.stopGroupTagsSyncTask = stopGroupTagsSyncTask;

console.log('[客户群标签] 模块已加载，所有函数已导出到 window 对象');

console.log('[客户群标签模块] 已加载');
