// ========== 客户群标签模块 ==========
console.log('[客户群标签] 脚本开始执行...', new Date().toISOString());

// 全局变量（使用 var 避免重复声明错误，或直接挂载到 window）
if (typeof window.window.groupTagsList === 'undefined') {
    window.window.groupTagsList = [];
}
if (typeof window.window.currentEditingGroupId === 'undefined') {
    window.window.currentEditingGroupId = null;
}
if (typeof window.window.currentEditingTagId === 'undefined') {
    window.window.currentEditingTagId = null;
}

// 确保 apiToken 可用
if (typeof apiToken === 'undefined') {
    var apiToken = localStorage.getItem('api_token') || 'crm-default-token';
    console.log('[客户群标签] 初始化 apiToken:', apiToken);
}

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
        showToast('开始同步客户群标签...', 'info');
        
        const res = await fetch(`/api/sync/group-tags?api_token=${apiToken}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({})
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('同步成功！', 'success');
            loadGroupTags(); // 重新加载列表
        } else {
            showToast(data.message || '同步失败', 'error');
        }
    } catch (error) {
        console.error('[客户群标签] 同步失败', error);
        showToast('同步失败，请检查网络连接', 'error');
    }
}

// 显示新建标签组对话框
function showAddGroupTagDialog() {
    window.currentEditingGroupId = null;
    document.getElementById('group-tag-dialog-title').textContent = '新建标签组';
    document.getElementById('group-tag-group-id').value = '';
    document.getElementById('group-tag-group-name').value = '';
    document.getElementById('group-tag-order').value = '1';
    
    // 清空并添加一个空的标签输入框
    const container = document.getElementById('group-tag-tags-container');
    container.innerHTML = '';
    addTagInput();
    
    document.getElementById('group-tag-dialog').style.display = 'flex';
}

// 编辑标签组
function editGroupTag(groupId) {
    const group = window.groupTagsList.find(g => g.group_id === groupId);
    if (!group) return;
    
    window.currentEditingGroupId = groupId;
    document.getElementById('group-tag-dialog-title').textContent = '编辑标签组';
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
    
    document.getElementById('group-tag-dialog').style.display = 'flex';
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
            closeGroupTagDialog();
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

// ========== 导出全局函数（确保 HTML 的 onclick 能访问）==========
window.loadGroupTags = loadGroupTags;
window.syncGroupTags = syncGroupTags;
window.showAddGroupTagDialog = showAddGroupTagDialog;
window.closeGroupTagDialog = closeGroupTagDialog;
window.saveGroupTag = saveGroupTag;
window.editGroupTag = editGroupTag;
window.deleteGroupTag = deleteGroupTag;
window.editTag = editTag;
window.saveEditTag = saveEditTag;
window.closeEditTagDialog = closeEditTagDialog;
window.deleteSingleTag = deleteSingleTag;
window.searchGroupTags = searchGroupTags;

console.log('[客户群标签] 模块已加载，所有函数已导出到 window 对象');

console.log('[客户群标签模块] 已加载');
