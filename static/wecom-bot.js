// ========================================
// 企微机器人模块 - 前端脚本
// 版本：v1.4 - 增强诊断
// 更新时间：2026-01-26
// ========================================

console.log('[企微机器人] 脚本开始加载 v1.4');

// ========== 全局变量 ==========
let currentWebhooks = {
    supplier: [],
    agent: []
};

console.log('[企微机器人] 全局变量初始化完成');

// ========== Webhook 管理 ==========

console.log('[企微机器人] 准备定义 showAddWebhookDialog 函数...');

// 显示添加群对话框
function showAddWebhookDialog(groupType) {
    const typeText = groupType === 'supplier' ? '供应商' : '代理商';
    const modal = document.createElement('div');
    modal.id = 'add-webhook-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 20px; width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; box-shadow: 0 24px 48px rgba(0, 0, 0, 0.24);">
            <div style="padding: 24px; border-bottom: 1px solid rgba(145, 158, 171, 0.12);">
                <h2 style="margin: 0; font-size: 20px; font-weight: 600; color: #212B36;">
                    <i class="fas fa-robot" style="color: #FF6B2C; margin-right: 8px;"></i>
                    添加${typeText}通知群
                </h2>
                <p style="margin: 8px 0 0 0; font-size: 13px; color: #637381;">
                    <i class="fas fa-info-circle"></i> 
                    群机器人仅支持<strong>内部群</strong>（纯员工群），不支持外部群
                </p>
            </div>
            
            <div style="padding: 24px;">
                <!-- 群名称 -->
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #212B36;">
                        群名称 <span style="color: #FF5630;">*</span>
                    </label>
                    <input type="text" id="webhook-group-name" placeholder="例如：财务通知群" 
                        style="width: 100%; padding: 10px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; transition: all 0.2s;"
                        onfocus="this.style.borderColor='#FF6B2C'; this.style.boxShadow='0 0 0 2px rgba(255, 107, 44, 0.1)'"
                        onblur="this.style.borderColor='rgba(145, 158, 171, 0.24)'; this.style.boxShadow='none'">
                </div>
                
                <!-- Webhook 地址 -->
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #212B36;">
                        Webhook 地址 <span style="color: #FF5630;">*</span>
                    </label>
                    <textarea id="webhook-url" rows="3" placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx" 
                        style="width: 100%; padding: 10px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 13px; font-family: 'Courier New', monospace; resize: vertical; transition: all 0.2s;"
                        onfocus="this.style.borderColor='#FF6B2C'; this.style.boxShadow='0 0 0 2px rgba(255, 107, 44, 0.1)'"
                        onblur="this.style.borderColor='rgba(145, 158, 171, 0.24)'; this.style.boxShadow='none'"></textarea>
                </div>
                
                <!-- 机器人用途 -->
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #212B36;">
                        机器人用途
                    </label>
                    <input type="text" id="webhook-purpose" placeholder="例如：财务结算通知、新品上线通知" 
                        style="width: 100%; padding: 10px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; transition: all 0.2s;"
                        onfocus="this.style.borderColor='#FF6B2C'; this.style.boxShadow='0 0 0 2px rgba(255, 107, 44, 0.1)'"
                        onblur="this.style.borderColor='rgba(145, 158, 171, 0.24)'; this.style.boxShadow='none'">
                </div>
                
                <!-- 备注 -->
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #212B36;">
                        备注
                    </label>
                    <textarea id="webhook-remark" rows="2" placeholder="可选，记录一些额外信息" 
                        style="width: 100%; padding: 10px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; resize: vertical; transition: all 0.2s;"
                        onfocus="this.style.borderColor='#FF6B2C'; this.style.boxShadow='0 0 0 2px rgba(255, 107, 44, 0.1)'"
                        onblur="this.style.borderColor='rgba(145, 158, 171, 0.24)'; this.style.boxShadow='none'"></textarea>
                </div>
                
                <!-- 操作说明 -->
                <div style="padding: 16px; background: rgba(255, 107, 44, 0.08); border-radius: 8px; border-left: 4px solid #FF6B2C; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; font-size: 14px; color: #212B36;">
                        <i class="fas fa-question-circle" style="color: #FF6B2C;"></i>
                        如何获取 Webhook 地址？
                    </h4>
                    <ol style="margin: 0; padding-left: 20px; font-size: 13px; color: #637381; line-height: 1.8;">
                        <li>在企业微信PC端或手机端，打开目标<strong>内部群</strong></li>
                        <li>点击群聊右上角的"..."，选择"添加群机器人"</li>
                        <li>输入机器人名称，点击"添加"</li>
                        <li>复制生成的 Webhook 地址，粘贴到上方输入框</li>
                    </ol>
                </div>
            </div>
            
            <div style="padding: 20px 28px; border-top: 1px solid rgba(0, 0, 0, 0.08); background: #F5F5F7; display: flex; justify-content: flex-end; gap: 12px;">
                <button onclick="closeAddWebhookDialog()" class="btn btn-secondary" style="
                    padding: 10px 24px !important; 
                    font-size: 15px !important;
                    background: rgba(0, 0, 0, 0.06) !important;
                    color: #1d1d1f !important;
                    border: none !important;
                    border-radius: 10px !important;
                    font-weight: 500 !important;
                    cursor: pointer !important;
                    transition: all 0.2s !important;
                ">
                    取消
                </button>
                <button onclick="saveWebhook('${groupType}')" class="btn btn-primary" style="
                    padding: 10px 24px !important; 
                    font-size: 15px !important;
                    background: linear-gradient(180deg, #007AFF 0%, #0051D5 100%) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 10px !important;
                    font-weight: 600 !important;
                    cursor: pointer !important;
                    transition: all 0.2s !important;
                    box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3) !important;
                ">
                    <i class="fas fa-check"></i> 确定
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 点击遮罩关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeAddWebhookDialog();
        }
    });
}

// 关闭添加群对话框
function closeAddWebhookDialog() {
    const modal = document.getElementById('add-webhook-modal');
    if (modal) {
        modal.remove();
    }
}

// 保存 Webhook 配置
async function saveWebhook(groupType) {
    const groupName = document.getElementById('webhook-group-name').value.trim();
    const webhookUrl = document.getElementById('webhook-url').value.trim();
    const purpose = document.getElementById('webhook-purpose').value.trim();
    const remark = document.getElementById('webhook-remark').value.trim();
    
    // 验证
    if (!groupName) {
        alert('请输入群名称');
        return;
    }
    
    if (!webhookUrl) {
        alert('请输入 Webhook 地址');
        return;
    }
    
    if (!webhookUrl.includes('qyapi.weixin.qq.com/cgi-bin/webhook/send?key=')) {
        alert('Webhook 地址格式不正确，请检查');
        return;
    }
    
    try {
        const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
        const response = await fetch(`/api/bot/webhooks?api_token=${apiToken}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                group_type: groupType,
                group_name: groupName,
                webhook_url: webhookUrl,
                purpose: purpose || '',
                remark: remark || ''
            })
        });
        
        const result = await response.json();
        console.log('[Webhook] API响应:', result);
        
        // 检查响应格式
        if (result.success === false) {
            // API返回错误
            throw new Error(result.message || '保存失败');
        }
        
        if (!response.ok) {
            // HTTP状态错误
            throw new Error(result.message || `HTTP ${response.status}`);
        }
        
        console.log('[Webhook] 保存成功:', result);
        
        // 关闭对话框
        closeAddWebhookDialog();
        
        // 显示成功提示
        showToast('保存成功', 'success');
        
        // 延迟刷新列表，确保对话框已关闭
        setTimeout(() => {
            loadWebhooks(groupType);
        }, 300);
        
    } catch (error) {
        console.error('[Webhook] 保存失败:', error);
        showToast('保存失败：' + error.message, 'error');
    }
}

// 加载 Webhook 列表
async function loadWebhooks(groupType) {
    console.log('[Webhook] ========== 开始加载列表 ==========');
    console.log('[Webhook] groupType:', groupType);
    try {
        const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
        const url = `/api/bot/webhooks?group_type=${groupType}&api_token=${apiToken}`;
        console.log('[Webhook] 请求 URL:', url);
        
        const response = await fetch(url);
        console.log('[Webhook] 响应状态:', response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('[Webhook] 原始数据:', data);
        console.log('[Webhook] 数据类型:', typeof data, '是否数组:', Array.isArray(data));
        
        // 处理API返回格式
        let webhookList = [];
        if (Array.isArray(data)) {
            // 直接返回数组
            webhookList = data;
        } else if (data.success === false) {
            // API返回错误
            console.error('[Webhook] API错误:', data.message);
            webhookList = [];
        } else if (data.data && Array.isArray(data.data)) {
            // 返回 {success: true, data: [...]}
            webhookList = data.data;
        }
        
        console.log('[Webhook] 处理后列表长度:', webhookList.length);
        
        currentWebhooks[groupType] = webhookList;
        
        // 渲染列表
        renderWebhookList(groupType, webhookList);
        console.log('[Webhook] ========== 加载完成 ==========');
        
    } catch (error) {
        console.error('[Webhook] ========== 加载失败 ==========');
        console.error('[Webhook] 错误:', error);
        // 渲染空列表
        renderWebhookList(groupType, []);
    }
}

// 渲染 Webhook 列表
function renderWebhookList(groupType, webhooks) {
    console.log('[Webhook] 开始渲染列表, groupType:', groupType, 'webhooks数量:', webhooks.length);
    
    const listId = groupType === 'supplier' ? 'supplier-webhook-list' : 'agent-webhook-list';
    const container = document.getElementById(listId);
    
    console.log('[Webhook] 容器元素:', container);
    
    if (!container) {
        console.error('[Webhook] 找不到容器元素:', listId);
        return;
    }
    
    if (webhooks.length === 0) {
        container.innerHTML = `
            <div class="text-center" style="padding: 40px; color: #999;">
                <i class="fas fa-robot" style="font-size: 48px; margin-bottom: 16px; opacity: 0.3;"></i>
                <p>暂无配置，点击"添加群"开始配置</p>
            </div>
        `;
        return;
    }
    
    let html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 20px;">';
    
    webhooks.forEach(webhook => {
        const statusBadge = webhook.status === 'active' 
            ? '<span style="padding: 4px 12px; background: rgba(52, 199, 89, 0.12); color: #1B5E20; border-radius: 8px; font-size: 12px; font-weight: 500;"><i class="fas fa-check-circle"></i> 正常</span>'
            : '<span style="padding: 4px 12px; background: rgba(255, 59, 48, 0.12); color: #B71C1C; border-radius: 8px; font-size: 12px; font-weight: 500;"><i class="fas fa-times-circle"></i> 停用</span>';
        
        html += `
            <div class="card" style="
                padding: 24px !important; 
                margin-bottom: 0 !important; 
                min-height: 280px; 
                display: flex; 
                flex-direction: column;
                background: white !important;
                border: 1px solid rgba(0, 0, 0, 0.12) !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 20px rgba(0, 0, 0, 0.12)'; this.style.borderColor='rgba(0, 122, 255, 0.3)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0, 0, 0, 0.06)'; this.style.borderColor='rgba(0, 0, 0, 0.12)';">
                <!-- 头部：标题和状态 -->
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; gap: 12px;">
                    <div style="flex: 1; min-width: 0;">
                        <h4 style="margin: 0 0 8px 0; font-size: 17px; font-weight: 600; color: #1d1d1f; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-comments" style="color: #007AFF; font-size: 16px; flex-shrink: 0;"></i>
                            <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${webhook.group_name}</span>
                        </h4>
                        ${webhook.purpose ? `<p style="margin: 0; font-size: 13px; color: #86868B; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${webhook.purpose}</p>` : ''}
                    </div>
                    <div style="flex-shrink: 0;">${statusBadge}</div>
                </div>
                
                <!-- Webhook 地址 -->
                <div style="padding: 12px; background: #F5F5F7; border-radius: 10px; margin-bottom: 16px;">
                    <p style="margin: 0; font-size: 11px; color: #636366; word-break: break-all; font-family: 'SF Mono', 'Monaco', monospace; line-height: 1.4;">
                        ${webhook.webhook_url.substring(0, 80)}...
                    </p>
                </div>
                
                ${webhook.remark ? `
                    <div style="padding: 12px; background: rgba(255, 149, 0, 0.08); border-left: 3px solid #FF9500; border-radius: 8px; margin-bottom: 16px;">
                        <p style="margin: 0; font-size: 13px; color: #8B5A00; line-height: 1.5;">
                            <i class="fas fa-sticky-note"></i> ${webhook.remark}
                        </p>
                    </div>
                ` : ''}
                
                <!-- 底部：时间和操作按钮 -->
                <div style="margin-top: auto; padding-top: 16px; border-top: 1px solid rgba(0, 0, 0, 0.06);">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                        <span style="font-size: 12px; color: #86868B; display: flex; align-items: center; gap: 6px;">
                            <i class="far fa-clock"></i>
                            <span>${new Date(webhook.created_at).toLocaleString('zh-CN', {month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'})}</span>
                        </span>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button onclick="testWebhook(${webhook.id})" style="
                            flex: 1; 
                            min-width: 0;
                            padding: 8px 14px !important; 
                            font-size: 13px !important;
                            background: rgba(0, 122, 255, 0.08) !important;
                            color: #007AFF !important;
                            border: 1px solid rgba(0, 122, 255, 0.2) !important;
                            border-radius: 8px !important;
                            font-weight: 500 !important;
                            cursor: pointer !important;
                            transition: all 0.2s !important;
                        " onmouseover="this.style.background='rgba(0, 122, 255, 0.15)'; this.style.borderColor='rgba(0, 122, 255, 0.4)';" onmouseout="this.style.background='rgba(0, 122, 255, 0.08)'; this.style.borderColor='rgba(0, 122, 255, 0.2)';">
                            <i class="fas fa-vial"></i> 测试
                        </button>
                        <button onclick="editWebhook(${webhook.id}, '${groupType}')" style="
                            flex: 1; 
                            min-width: 0;
                            padding: 8px 14px !important; 
                            font-size: 13px !important;
                            background: rgba(0, 122, 255, 0.08) !important;
                            color: #007AFF !important;
                            border: 1px solid rgba(0, 122, 255, 0.2) !important;
                            border-radius: 8px !important;
                            font-weight: 500 !important;
                            cursor: pointer !important;
                            transition: all 0.2s !important;
                        " onmouseover="this.style.background='rgba(0, 122, 255, 0.15)'; this.style.borderColor='rgba(0, 122, 255, 0.4)';" onmouseout="this.style.background='rgba(0, 122, 255, 0.08)'; this.style.borderColor='rgba(0, 122, 255, 0.2)';">
                            <i class="fas fa-edit"></i> 编辑
                        </button>
                        <button onclick="deleteWebhook(${webhook.id}, '${groupType}')" style="
                            flex: 1; 
                            min-width: 0;
                            padding: 8px 14px !important; 
                            font-size: 13px !important;
                            background: rgba(255, 59, 48, 0.08) !important;
                            color: #FF3B30 !important;
                            border: 1px solid rgba(255, 59, 48, 0.2) !important;
                            border-radius: 8px !important;
                            font-weight: 500 !important;
                            cursor: pointer !important;
                            transition: all 0.2s !important;
                        " onmouseover="this.style.background='rgba(255, 59, 48, 0.15)'; this.style.borderColor='rgba(255, 59, 48, 0.4)';" onmouseout="this.style.background='rgba(255, 59, 48, 0.08)'; this.style.borderColor='rgba(255, 59, 48, 0.2)';">
                            <i class="fas fa-trash"></i> 删除
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// 测试 Webhook
async function testWebhook(webhookId) {
    if (!confirm('确定要发送测试消息吗？')) {
        return;
    }
    
    try {
        const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
        const response = await fetch(`/api/bot/webhooks/${webhookId}/test?api_token=${apiToken}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
        } else {
            showToast(result.message, 'error');
        }
        
    } catch (error) {
        console.error('[Webhook] 测试失败:', error);
        showToast('测试失败：' + error.message, 'error');
    }
}

// 删除 Webhook
async function deleteWebhook(webhookId, groupType) {
    if (!confirm('确定要删除这个群机器人配置吗？')) {
        return;
    }
    
    try {
        const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
        const response = await fetch(`/api/bot/webhooks/${webhookId}?api_token=${apiToken}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('删除失败');
        
        // 刷新列表
        loadWebhooks(groupType);
        
        showToast('删除成功', 'success');
        
    } catch (error) {
        console.error('[Webhook] 删除失败:', error);
        alert('删除失败：' + error.message);
    }
}

// 编辑 Webhook
async function editWebhook(webhookId, groupType) {
    try {
        const webhook = currentWebhooks[groupType].find(w => w.id === webhookId);
        if (!webhook) {
            alert('找不到Webhook信息');
            return;
        }
        
        const typeText = groupType === 'supplier' ? '供应商' : '代理商';
        const modal = document.createElement('div');
        modal.id = 'edit-webhook-modal';
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.5); display: flex;
            align-items: center; justify-content: center; z-index: 10000;
        `;
        
        modal.innerHTML = `
            <div style="background: white; border-radius: 20px; width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; box-shadow: 0 24px 48px rgba(0, 0, 0, 0.24);">
                <div style="padding: 24px; border-bottom: 1px solid rgba(145, 158, 171, 0.12);">
                    <h2 style="margin: 0; font-size: 20px; font-weight: 600; color: #212B36;">
                        <i class="fas fa-edit" style="color: #FF6B2C; margin-right: 8px;"></i>
                        编辑${typeText}通知群
                    </h2>
                </div>
                
                <div style="padding: 24px;">
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500; color: #637381;">群名称 <span style="color: #ff4842;">*</span></label>
                        <input type="text" id="edit-webhook-name" value="${webhook.group_name || ''}" placeholder="例如：核心供应商群" 
                            style="width: 100%; padding: 12px; border: 1px solid #DFE3E8; border-radius: 8px; font-size: 14px;">
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500; color: #637381;">Webhook 地址 <span style="color: #ff4842;">*</span></label>
                        <textarea id="edit-webhook-url" placeholder="从企业微信群聊中复制" rows="3"
                            style="width: 100%; padding: 12px; border: 1px solid #DFE3E8; border-radius: 8px; font-size: 14px; resize: vertical;">${webhook.webhook_url || ''}</textarea>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500; color: #637381;">机器人用途</label>
                        <input type="text" id="edit-webhook-purpose" value="${webhook.purpose || ''}" placeholder="例如：发送每日供应动态" 
                            style="width: 100%; padding: 12px; border: 1px solid #DFE3E8; border-radius: 8px; font-size: 14px;">
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500; color: #637381;">备注</label>
                        <textarea id="edit-webhook-remark" placeholder="其他说明..." rows="2"
                            style="width: 100%; padding: 12px; border: 1px solid #DFE3E8; border-radius: 8px; font-size: 14px; resize: vertical;">${webhook.remark || ''}</textarea>
                    </div>
                </div>
                
                <div style="padding: 16px 24px; background: #F4F6F8; border-radius: 0 0 12px 12px; display: flex; justify-content: flex-end; gap: 12px;">
                    <button onclick="document.getElementById('edit-webhook-modal').remove()" 
                        style="padding: 10px 24px; background: white; border: 1px solid #DFE3E8; border-radius: 8px; color: #637381; cursor: pointer; font-size: 14px; font-weight: 500;">
                        取消
                    </button>
                    <button onclick="saveEditedWebhook(${webhookId}, '${groupType}')" 
                        style="padding: 10px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 8px; color: white; cursor: pointer; font-size: 14px; font-weight: 500;">
                        <i class="fas fa-save"></i> 保存
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 点击背景关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
    } catch (error) {
        console.error('[Webhook] 编辑失败:', error);
        alert('编辑失败：' + error.message);
    }
}

// 保存编辑
async function saveEditedWebhook(webhookId, groupType) {
    try {
        const group_name = document.getElementById('edit-webhook-name').value.trim();
        const webhook_url = document.getElementById('edit-webhook-url').value.trim();
        const purpose = document.getElementById('edit-webhook-purpose').value.trim();
        const remark = document.getElementById('edit-webhook-remark').value.trim();
        
        if (!group_name || !webhook_url) {
            alert('请填写群名称和 Webhook 地址');
            return;
        }
        
        const response = await fetch(`/api/bot/webhooks/${webhookId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                group_name,
                webhook_url,
                purpose: purpose || '',
                remark: remark || ''
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || '保存失败');
        }
        
        console.log('[Webhook] 编辑成功');
        
        // 关闭对话框
        document.getElementById('edit-webhook-modal')?.remove();
        
        // 刷新列表
        setTimeout(() => {
            loadWebhooks(groupType);
        }, 300);
        
        showToast('保存成功', 'success');
        
    } catch (error) {
        console.error('[Webhook] 保存失败:', error);
        alert('保存失败：' + error.message);
    }
}

// 切换 Webhook 状态
async function toggleWebhookStatus(webhookId, currentStatus, groupType) {
    try {
        const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
        const statusText = newStatus === 'active' ? '启用' : '停用';
        
        if (!confirm(`确定要${statusText}这个机器人吗？`)) {
            return;
        }
        
        const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
        const response = await fetch(`/api/bot/webhooks/${webhookId}/toggle?api_token=${apiToken}`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('操作失败');
        
        loadWebhooks(groupType);
        showToast(`${statusText}成功`, 'success');
        
    } catch (error) {
        console.error('[Webhook] 状态切换失败:', error);
        alert('操作失败：' + error.message);
    }
}

// ========== 通知消息管理 ==========

// 显示创建通知对话框
function showCreateNotificationDialog(groupType) {
    const typeText = groupType === 'supplier' ? '供应商' : '代理商';
    const webhooks = currentWebhooks[groupType];
    
    if (webhooks.length === 0) {
        alert('请先添加群机器人配置');
        return;
    }
    
    const modal = document.createElement('div');
    modal.id = 'create-notification-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        overflow-y: auto;
    `;
    
    // 生成群选择选项
    const webhookOptions = webhooks.map(w => 
        `<option value="${w.id}">${w.group_name} - ${w.purpose || '未设置用途'}</option>`
    ).join('');
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 12px; width: 90%; max-width: 800px; max-height: 90vh; overflow-y: auto; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15); margin: 20px;">
            <div style="padding: 24px; border-bottom: 1px solid rgba(145, 158, 171, 0.12); position: sticky; top: 0; background: white; z-index: 1;">
                <h2 style="margin: 0; font-size: 20px; font-weight: 600; color: #212B36;">
                    <i class="fas fa-paper-plane" style="color: #FF6B2C; margin-right: 8px;"></i>
                    创建${typeText}通知
                </h2>
            </div>
            
            <div style="padding: 24px;">
                <!-- 选择目标群 -->
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #212B36;">
                        目标群 <span style="color: #FF5630;">*</span>
                    </label>
                    <select id="notification-webhook-id" multiple size="5" 
                        style="width: 100%; padding: 10px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px;">
                        ${webhookOptions}
                    </select>
                    <p style="margin: 4px 0 0 0; font-size: 12px; color: #637381;">
                        <i class="fas fa-info-circle"></i> 按住 Ctrl/Command 可多选
                    </p>
                </div>
                
                <!-- 消息类型 -->
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #212B36;">
                        消息类型 <span style="color: #FF5630;">*</span>
                    </label>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                        <button type="button" class="msg-type-btn active" data-type="text" onclick="selectMessageType('text')" 
                            style="padding: 12px; border: 2px solid #FF6B2C; border-radius: 8px; background: rgba(255, 107, 44, 0.08); color: #212B36; font-size: 14px; cursor: pointer; transition: all 0.2s;">
                            <i class="fas fa-font"></i> 文本
                        </button>
                        <button type="button" class="msg-type-btn" data-type="markdown" onclick="selectMessageType('markdown')" 
                            style="padding: 12px; border: 2px solid rgba(145, 158, 171, 0.24); border-radius: 8px; background: white; color: #212B36; font-size: 14px; cursor: pointer; transition: all 0.2s;">
                            <i class="fab fa-markdown"></i> Markdown
                        </button>
                        <button type="button" class="msg-type-btn" data-type="news" onclick="selectMessageType('news')" 
                            style="padding: 12px; border: 2px solid rgba(145, 158, 171, 0.24); border-radius: 8px; background: white; color: #212B36; font-size: 14px; cursor: pointer; transition: all 0.2s;">
                            <i class="fas fa-newspaper"></i> 图文
                        </button>
                    </div>
                </div>
                
                <!-- 消息内容 - 文本 -->
                <div id="content-text" style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #212B36;">
                        消息内容 <span style="color: #FF5630;">*</span>
                    </label>
                    <textarea id="notification-content-text" rows="8" placeholder="请输入消息内容，最多2048字节（约700汉字）" 
                        style="width: 100%; padding: 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; resize: vertical;"
                        maxlength="700"></textarea>
                    <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                        <p style="margin: 0; font-size: 12px; color: #637381;">
                            <i class="fas fa-lightbulb"></i> 支持@成员，在下方配置
                        </p>
                        <p style="margin: 0; font-size: 12px; color: #919EAB;">
                            <span id="text-char-count">0</span> / 700 字
                        </p>
                    </div>
                </div>
                
                <!-- 消息内容 - Markdown -->
                <div id="content-markdown" style="margin-bottom: 20px; display: none;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #212B36;">
                        Markdown 内容 <span style="color: #FF5630;">*</span>
                    </label>
                    <textarea id="notification-content-markdown" rows="10" placeholder="支持 Markdown 语法：# 标题、**粗体**、[链接](url)、> 引用等" 
                        style="width: 100%; padding: 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 13px; font-family: 'Courier New', monospace; resize: vertical;"></textarea>
                </div>
                
                <!-- 消息内容 - 图文 -->
                <div id="content-news" style="display: none;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #212B36;">
                        图文内容 <span style="color: #FF5630;">*</span>
                    </label>
                    <div id="news-items">
                        <div class="news-item" style="margin-bottom: 16px; padding: 16px; border: 1px solid rgba(145, 158, 171, 0.12); border-radius: 8px; background: #F9FAFB;">
                            <input type="text" class="news-title" placeholder="标题（必填）" 
                                style="width: 100%; padding: 8px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; margin-bottom: 8px;">
                            <input type="text" class="news-url" placeholder="跳转链接（必填）" 
                                style="width: 100%; padding: 8px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; margin-bottom: 8px;">
                            <input type="text" class="news-picurl" placeholder="图片链接（可选）" 
                                style="width: 100%; padding: 8px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; margin-bottom: 8px;">
                            <textarea class="news-desc" rows="2" placeholder="描述（可选）" 
                                style="width: 100%; padding: 8px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; resize: vertical;"></textarea>
                        </div>
                    </div>
                    <button type="button" onclick="addNewsItem()" 
                        style="padding: 8px 16px; border: 1px dashed rgba(145, 158, 171, 0.32); border-radius: 6px; background: white; color: #637381; font-size: 13px; cursor: pointer;">
                        <i class="fas fa-plus"></i> 添加图文（最多8条）
                    </button>
                </div>
                
                <!-- @ 成员配置 -->
                <div style="margin-bottom: 20px; padding: 16px; background: rgba(255, 171, 0, 0.08); border-radius: 8px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #212B36;">
                        <i class="fas fa-at"></i> @ 成员
                    </label>
                    <div style="display: flex; gap: 12px; align-items: center;">
                        <label style="display: flex; align-items: center; cursor: pointer;">
                            <input type="checkbox" id="mention-all" style="margin-right: 6px;">
                            <span style="font-size: 13px; color: #212B36;">@所有人</span>
                        </label>
                        <span style="color: #DFE3E8;">|</span>
                        <input type="text" id="mention-users" placeholder="指定成员userid，用逗号分隔" 
                            style="flex: 1; padding: 8px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 13px;">
                    </div>
                </div>
                
                <!-- 发送时间 -->
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #212B36;">
                        发送时间 <span style="color: #FF5630;">*</span>
                    </label>
                    <div style="display: flex; gap: 12px; align-items: center;">
                        <label style="display: flex; align-items: center; cursor: pointer;">
                            <input type="radio" name="send-time" value="now" checked style="margin-right: 6px;">
                            <span style="font-size: 14px; color: #212B36;">立即发送</span>
                        </label>
                        <label style="display: flex; align-items: center; cursor: pointer;">
                            <input type="radio" name="send-time" value="scheduled" style="margin-right: 6px;" onchange="toggleScheduledTime()">
                            <span style="font-size: 14px; color: #212B36;">定时发送</span>
                        </label>
                        <input type="datetime-local" id="scheduled-time" disabled 
                            style="flex: 1; padding: 8px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 13px;">
                    </div>
                </div>
                
                <!-- 预览区域 -->
                <div style="padding: 16px; background: #F9FAFB; border-radius: 8px; border: 1px solid rgba(145, 158, 171, 0.12);">
                    <h4 style="margin: 0 0 12px 0; font-size: 14px; font-weight: 500; color: #212B36;">
                        <i class="fas fa-eye"></i> 消息预览
                    </h4>
                    <div id="message-preview" style="padding: 12px; background: white; border-radius: 6px; min-height: 60px; font-size: 13px; color: #637381;">
                        <p style="margin: 0; text-align: center; opacity: 0.5;">输入内容后实时预览...</p>
                    </div>
                </div>
            </div>
            
            <div style="padding: 16px 24px; border-top: 1px solid rgba(145, 158, 171, 0.12); display: flex; justify-content: flex-end; gap: 12px; position: sticky; bottom: 0; background: white;">
                <button onclick="closeCreateNotificationDialog()" 
                    style="padding: 10px 24px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; background: white; color: #637381; font-size: 14px; cursor: pointer; transition: all 0.2s;"
                    onmouseover="this.style.background='#F4F6F8'" 
                    onmouseout="this.style.background='white'">
                    取消
                </button>
                <button onclick="sendNotification('${groupType}')" 
                    style="padding: 10px 24px; border: none; border-radius: 6px; background: #FF6B2C; color: white; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; box-shadow: 0 2px 8px rgba(255, 107, 44, 0.24);"
                    onmouseover="this.style.background='#E85D1C'; this.style.boxShadow='0 4px 12px rgba(255, 107, 44, 0.32)'" 
                    onmouseout="this.style.background='#FF6B2C'; this.style.boxShadow='0 2px 8px rgba(255, 107, 44, 0.24)'">
                    <i class="fas fa-paper-plane"></i> 发送
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 添加字数统计
    const textArea = document.getElementById('notification-content-text');
    const charCount = document.getElementById('text-char-count');
    textArea.addEventListener('input', () => {
        charCount.textContent = textArea.value.length;
    });
    
    // 点击遮罩关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeCreateNotificationDialog();
        }
    });
}

// 关闭创建通知对话框
function closeCreateNotificationDialog() {
    const modal = document.getElementById('create-notification-modal');
    if (modal) {
        modal.remove();
    }
}

// 选择消息类型
function selectMessageType(type) {
    // 更新按钮状态
    const buttons = document.querySelectorAll('.msg-type-btn');
    buttons.forEach(btn => {
        if (btn.getAttribute('data-type') === type) {
            btn.style.borderColor = '#FF6B2C';
            btn.style.background = 'rgba(255, 107, 44, 0.08)';
            btn.classList.add('active');
        } else {
            btn.style.borderColor = 'rgba(145, 158, 171, 0.24)';
            btn.style.background = 'white';
            btn.classList.remove('active');
        }
    });
    
    // 显示对应的内容输入区
    document.getElementById('content-text').style.display = type === 'text' ? 'block' : 'none';
    document.getElementById('content-markdown').style.display = type === 'markdown' ? 'block' : 'none';
    document.getElementById('content-news').style.display = type === 'news' ? 'block' : 'none';
}

// 添加图文项
function addNewsItem() {
    const container = document.getElementById('news-items');
    const items = container.querySelectorAll('.news-item');
    if (items.length >= 8) {
        alert('最多只能添加8条图文');
        return;
    }
    
    const newItem = document.createElement('div');
    newItem.className = 'news-item';
    newItem.style.cssText = 'margin-bottom: 16px; padding: 16px; border: 1px solid rgba(145, 158, 171, 0.12); border-radius: 8px; background: #F9FAFB; position: relative;';
    newItem.innerHTML = `
        <button type="button" onclick="this.parentElement.remove()" 
            style="position: absolute; top: 8px; right: 8px; padding: 4px 8px; border: none; background: rgba(255, 86, 48, 0.12); color: #FF5630; border-radius: 4px; font-size: 12px; cursor: pointer;">
            <i class="fas fa-times"></i>
        </button>
        <input type="text" class="news-title" placeholder="标题（必填）" 
            style="width: 100%; padding: 8px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; margin-bottom: 8px;">
        <input type="text" class="news-url" placeholder="跳转链接（必填）" 
            style="width: 100%; padding: 8px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; margin-bottom: 8px;">
        <input type="text" class="news-picurl" placeholder="图片链接（可选）" 
            style="width: 100%; padding: 8px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; margin-bottom: 8px;">
        <textarea class="news-desc" rows="2" placeholder="描述（可选）" 
            style="width: 100%; padding: 8px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; font-size: 14px; resize: vertical;"></textarea>
    `;
    container.appendChild(newItem);
}

// 切换定时发送
function toggleScheduledTime() {
    const scheduledRadio = document.querySelector('input[name="send-time"][value="scheduled"]');
    const scheduledTimeInput = document.getElementById('scheduled-time');
    scheduledTimeInput.disabled = !scheduledRadio.checked;
}

// 发送通知
async function sendNotification(groupType) {
    // 获取选中的群
    const select = document.getElementById('notification-webhook-id');
    const selectedWebhooks = Array.from(select.selectedOptions).map(option => parseInt(option.value));
    
    if (selectedWebhooks.length === 0) {
        alert('请选择目标群');
        return;
    }
    
    // 获取消息类型
    const msgType = document.querySelector('.msg-type-btn.active').getAttribute('data-type');
    
    // 构建消息内容
    let content = {};
    
    if (msgType === 'text') {
        const text = document.getElementById('notification-content-text').value.trim();
        if (!text) {
            alert('请输入消息内容');
            return;
        }
        
        content = {
            msgtype: 'text',
            text: {
                content: text
            }
        };
        
        // 处理@成员
        const mentionAll = document.getElementById('mention-all').checked;
        const mentionUsers = document.getElementById('mention-users').value.trim();
        
        if (mentionAll) {
            content.text.mentioned_list = ['@all'];
        } else if (mentionUsers) {
            content.text.mentioned_list = mentionUsers.split(',').map(u => u.trim());
        }
        
    } else if (msgType === 'markdown') {
        const markdown = document.getElementById('notification-content-markdown').value.trim();
        if (!markdown) {
            alert('请输入 Markdown 内容');
            return;
        }
        
        content = {
            msgtype: 'markdown',
            markdown: {
                content: markdown
            }
        };
        
    } else if (msgType === 'news') {
        const newsItems = document.querySelectorAll('.news-item');
        const articles = [];
        
        newsItems.forEach(item => {
            const title = item.querySelector('.news-title').value.trim();
            const url = item.querySelector('.news-url').value.trim();
            const picurl = item.querySelector('.news-picurl').value.trim();
            const desc = item.querySelector('.news-desc').value.trim();
            
            if (title && url) {
                articles.push({
                    title,
                    url,
                    picurl: picurl || '',
                    description: desc || ''
                });
            }
        });
        
        if (articles.length === 0) {
            alert('请至少填写一条图文（标题和链接必填）');
            return;
        }
        
        content = {
            msgtype: 'news',
            news: {
                articles
            }
        };
    }
    
    // 获取发送时间
    const sendTimeType = document.querySelector('input[name="send-time"]:checked').value;
    let scheduledTime = null;
    
    if (sendTimeType === 'scheduled') {
        const timeInput = document.getElementById('scheduled-time').value;
        if (!timeInput) {
            alert('请选择定时发送时间');
            return;
        }
        scheduledTime = new Date(timeInput).getTime();
    }
    
    // 发送请求
    try {
        const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
        const response = await fetch(`/api/bot/notifications?api_token=${apiToken}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                group_type: groupType,
                title: '',
                content: JSON.stringify(content),
                msg_type: msgType,
                target_webhooks: selectedWebhooks,
                mentioned_list: content.text?.mentioned_list || null,
                send_mode: sendTimeType === 'scheduled' ? 'auto' : 'manual',
                send_time: scheduledTime,
                need_approval: 0
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '发送失败');
        }
        
        const result = await response.json();
        console.log('[通知] 发送成功:', result);
        
        // 关闭对话框
        closeCreateNotificationDialog();
        
        // 刷新通知列表
        loadNotifications(groupType);
        
        // 显示成功提示
        const message = sendTimeType === 'scheduled' 
            ? '定时通知已创建，将在指定时间发送' 
            : `通知已发送到 ${selectedWebhooks.length} 个群`;
        showToast(message, 'success');
        
    } catch (error) {
        console.error('[通知] 发送失败:', error);
        alert('发送失败：' + error.message);
    }
}

// 加载通知列表
async function loadNotifications(groupType) {
    try {
        const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
        const response = await fetch(`/api/bot/notifications?group_type=${groupType}&limit=50&api_token=${apiToken}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // 处理API返回格式
        let notificationList = [];
        if (Array.isArray(data)) {
            notificationList = data;
        } else if (data.success === false) {
            console.error('[通知] API错误:', data.message);
            notificationList = [];
        } else if (data.data && Array.isArray(data.data)) {
            notificationList = data.data;
        }
        
        // 渲染列表
        renderNotificationList(groupType, notificationList);
        
    } catch (error) {
        console.error('[通知] 加载失败:', error);
        // 渲染空列表
        renderNotificationList(groupType, []);
    }
}

// 渲染通知列表
function renderNotificationList(groupType, notifications) {
    const listId = groupType === 'supplier' ? 'supplier-notification-list' : 'agent-notification-list';
    const container = document.getElementById(listId);
    if (!container) return;
    
    if (notifications.length === 0) {
        container.innerHTML = `
            <div class="text-center" style="padding: 40px; color: #999;">
                <i class="fas fa-history" style="font-size: 48px; margin-bottom: 16px; opacity: 0.3;"></i>
                <p>暂无通知记录</p>
            </div>
        `;
        return;
    }
    
    let html = '<div style="display: flex; flex-direction: column; gap: 12px;">';
    
    notifications.forEach(notification => {
        const statusInfo = getNotificationStatusInfo(notification.status);
        const content = JSON.parse(notification.content);
        const contentPreview = getContentPreview(content);
        
        html += `
            <div style="border: 1px solid rgba(145, 158, 171, 0.12); border-radius: 8px; padding: 16px; background: white; transition: all 0.2s;"
                onmouseover="this.style.boxShadow='0 2px 8px rgba(145, 158, 171, 0.12)'" 
                onmouseout="this.style.boxShadow='none'">
                
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <span style="padding: 4px 10px; background: ${statusInfo.bgColor}; color: ${statusInfo.color}; border-radius: 4px; font-size: 12px; font-weight: 500;">
                                ${statusInfo.icon} ${statusInfo.text}
                            </span>
                            <span style="padding: 4px 10px; background: rgba(145, 158, 171, 0.08); color: #637381; border-radius: 4px; font-size: 12px;">
                                ${content.msgtype}
                            </span>
                        </div>
                        <p style="margin: 4px 0 0 0; font-size: 14px; color: #212B36; line-height: 1.6;">
                            ${contentPreview}
                        </p>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid rgba(145, 158, 171, 0.08);">
                    <div style="display: flex; align-items: center; gap: 16px; font-size: 12px; color: #919EAB;">
                        <span>
                            <i class="far fa-clock"></i>
                            ${new Date(notification.created_at).toLocaleString('zh-CN')}
                        </span>
                        ${notification.scheduled_time ? `
                            <span>
                                <i class="far fa-calendar-alt"></i>
                                ${new Date(notification.scheduled_time).toLocaleString('zh-CN')}
                            </span>
                        ` : ''}
                    </div>
                    <button onclick="viewNotificationDetail(${notification.id})" 
                        style="padding: 6px 12px; border: 1px solid rgba(145, 158, 171, 0.24); border-radius: 6px; background: white; color: #637381; font-size: 12px; cursor: pointer; transition: all 0.2s;"
                        onmouseover="this.style.background='#F4F6F8'" 
                        onmouseout="this.style.background='white'">
                        <i class="fas fa-eye"></i> 详情
                    </button>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// 获取通知状态信息
function getNotificationStatusInfo(status) {
    const statusMap = {
        'pending': { text: '待发送', icon: '<i class="far fa-clock"></i>', color: '#7A4F01', bgColor: 'rgba(255, 171, 0, 0.12)' },
        'sending': { text: '发送中', icon: '<i class="fas fa-spinner fa-spin"></i>', color: '#006C9C', bgColor: 'rgba(0, 184, 217, 0.12)' },
        'sent': { text: '已发送', icon: '<i class="fas fa-check-circle"></i>', color: '#005249', bgColor: 'rgba(0, 167, 111, 0.12)' },
        'failed': { text: '发送失败', icon: '<i class="fas fa-times-circle"></i>', color: '#7A0C2E', bgColor: 'rgba(255, 86, 48, 0.12)' }
    };
    return statusMap[status] || statusMap['pending'];
}

// 获取内容预览
function getContentPreview(content) {
    if (content.msgtype === 'text') {
        return content.text.content.substring(0, 100) + (content.text.content.length > 100 ? '...' : '');
    } else if (content.msgtype === 'markdown') {
        return content.markdown.content.substring(0, 100) + (content.markdown.content.length > 100 ? '...' : '');
    } else if (content.msgtype === 'news') {
        return `图文消息（${content.news.articles.length}条）：${content.news.articles[0].title}`;
    }
    return '消息内容';
}

// 查看通知详情
async function viewNotificationDetail(notificationId) {
    try {
        const apiToken = localStorage.getItem('api_token') || 'crm-default-token';
        const response = await fetch(`/api/bot/notifications/${notificationId}?api_token=${apiToken}`);
        const notification = await response.json();
        
        if (!notification || notification.success === false) {
            alert('获取通知详情失败');
            return;
        }
        
        // 解析内容
        let contentObj = {};
        try {
            contentObj = JSON.parse(notification.content);
        } catch (e) {
            contentObj = { text: { content: notification.content } };
        }
        
        // 构建详情对话框
        const modal = document.createElement('div');
        modal.id = 'notification-detail-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            overflow-y: auto;
        `;
        
        const statusInfo = getNotificationStatusInfo(notification.status);
        
        // 构建目标群列表
        let webhooksHtml = '';
        if (notification.webhooks && notification.webhooks.length > 0) {
            webhooksHtml = notification.webhooks.map(w => `
                <div style="padding: 8px 12px; background: #F9FAFB; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 13px; color: #212B36;">${w.group_name}</span>
                    <span style="padding: 2px 8px; background: ${w.status === 'active' ? 'rgba(0, 167, 111, 0.12)' : 'rgba(255, 86, 48, 0.12)'}; color: ${w.status === 'active' ? '#005249' : '#7A0C2E'}; border-radius: 4px; font-size: 11px;">${w.status === 'active' ? '正常' : '停用'}</span>
                </div>
            `).join('');
        } else {
            webhooksHtml = '<p style="color: #919EAB; font-size: 13px;">无目标群</p>';
        }
        
        // 构建发送记录
        let sendLogsHtml = '';
        if (notification.send_logs && notification.send_logs.length > 0) {
            sendLogsHtml = notification.send_logs.map(log => {
                const logStatusInfo = log.status === 'success' 
                    ? { text: '成功', icon: '<i class="fas fa-check-circle"></i>', color: '#005249', bgColor: 'rgba(0, 167, 111, 0.12)' }
                    : { text: '失败', icon: '<i class="fas fa-times-circle"></i>', color: '#7A0C2E', bgColor: 'rgba(255, 86, 48, 0.12)' };
                
                return `
                    <div style="padding: 12px; background: #F9FAFB; border-radius: 6px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 14px; font-weight: 500; color: #212B36;">${log.webhook_name}</span>
                            <span style="padding: 4px 10px; background: ${logStatusInfo.bgColor}; color: ${logStatusInfo.color}; border-radius: 4px; font-size: 12px;">
                                ${logStatusInfo.icon} ${logStatusInfo.text}
                            </span>
                        </div>
                        <div style="font-size: 12px; color: #637381;">
                            <div>发送时间：${new Date(log.send_time).toLocaleString('zh-CN')}</div>
                            ${log.error_msg ? `<div style="color: #FF5630; margin-top: 4px;">错误：${log.error_msg}</div>` : ''}
                            ${log.response && log.response.errmsg ? `<div style="color: #637381; margin-top: 4px;">响应：${log.response.errmsg}</div>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            sendLogsHtml = '<p style="color: #919EAB; font-size: 13px;">暂无发送记录</p>';
        }
        
        // 消息内容预览
        let contentPreview = '';
        if (contentObj.msgtype === 'text') {
            contentPreview = `<p style="white-space: pre-wrap;">${contentObj.text.content}</p>`;
        } else if (contentObj.msgtype === 'markdown') {
            contentPreview = `<pre style="white-space: pre-wrap; font-family: 'Courier New', monospace;">${contentObj.markdown.content}</pre>`;
        } else if (contentObj.msgtype === 'news') {
            contentPreview = contentObj.news.articles.map(a => `
                <div style="padding: 8px; border: 1px solid rgba(145, 158, 171, 0.12); border-radius: 4px; margin-bottom: 8px;">
                    <div style="font-weight: 500;">${a.title}</div>
                    ${a.description ? `<div style="font-size: 12px; color: #637381; margin-top: 4px;">${a.description}</div>` : ''}
                    <div style="font-size: 12px; color: #00B8D9; margin-top: 4px;">${a.url}</div>
                </div>
            `).join('');
        }
        
        modal.innerHTML = `
            <div style="background: white; border-radius: 12px; width: 90%; max-width: 800px; max-height: 90vh; overflow-y: auto; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15); margin: 20px;">
                <div style="padding: 24px; border-bottom: 1px solid rgba(145, 158, 171, 0.12); position: sticky; top: 0; background: white; z-index: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h2 style="margin: 0; font-size: 20px; font-weight: 600; color: #212B36;">
                            <i class="fas fa-info-circle" style="color: #FF6B2C; margin-right: 8px;"></i>
                            通知详情
                        </h2>
                        <button onclick="closeNotificationDetailDialog()" style="border: none; background: none; font-size: 24px; color: #919EAB; cursor: pointer; padding: 0; width: 32px; height: 32px;">×</button>
                    </div>
                    <div style="margin-top: 12px;">
                        <span style="padding: 4px 12px; background: ${statusInfo.bgColor}; color: ${statusInfo.color}; border-radius: 4px; font-size: 13px; font-weight: 500;">
                            ${statusInfo.icon} ${statusInfo.text}
                        </span>
                        <span style="margin-left: 12px; font-size: 13px; color: #637381;">
                            <i class="far fa-clock"></i> ${new Date(notification.created_at).toLocaleString('zh-CN')}
                        </span>
                    </div>
                </div>
                
                <div style="padding: 24px;">
                    <!-- 消息内容 -->
                    <div style="margin-bottom: 24px;">
                        <h3 style="margin: 0 0 12px 0; font-size: 16px; font-weight: 600; color: #212B36;">消息内容</h3>
                        <div style="padding: 16px; background: #F9FAFB; border-radius: 8px; font-size: 14px; color: #212B36;">
                            ${contentPreview}
                        </div>
                        ${contentObj.text?.mentioned_list?.length > 0 ? `
                            <div style="margin-top: 8px; font-size: 13px; color: #637381;">
                                <i class="fas fa-at"></i> @成员：${contentObj.text.mentioned_list.join(', ')}
                            </div>
                        ` : ''}
                    </div>
                    
                    <!-- 目标群 -->
                    <div style="margin-bottom: 24px;">
                        <h3 style="margin: 0 0 12px 0; font-size: 16px; font-weight: 600; color: #212B36;">目标群（${notification.webhooks?.length || 0}个）</h3>
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            ${webhooksHtml}
                        </div>
                    </div>
                    
                    <!-- 发送记录 -->
                    <div>
                        <h3 style="margin: 0 0 12px 0; font-size: 16px; font-weight: 600; color: #212B36;">发送记录</h3>
                        ${sendLogsHtml}
                    </div>
                </div>
                
                <div style="padding: 16px 24px; border-top: 1px solid rgba(145, 158, 171, 0.12); position: sticky; bottom: 0; background: white;">
                    <button onclick="closeNotificationDetailDialog()" 
                        style="width: 100%; padding: 12px; border: none; border-radius: 6px; background: #F4F6F8; color: #637381; font-size: 14px; font-weight: 500; cursor: pointer;">
                        关闭
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 点击遮罩关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeNotificationDetailDialog();
            }
        });
        
    } catch (error) {
        console.error('[通知] 获取详情失败:', error);
        alert('获取详情失败：' + error.message);
    }
}

// 关闭通知详情对话框
function closeNotificationDetailDialog() {
    const modal = document.getElementById('notification-detail-modal');
    if (modal) {
        modal.remove();
    }
}

// ========== 工具函数 ==========

// 显示提示
function showToast(message, type = 'info') {
    const colors = {
        'success': '#00A76F',
        'error': '#FF5630',
        'warning': '#FFAB00',
        'info': '#00B8D9'
    };
    
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${colors[type] || colors.info};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10001;
        font-size: 14px;
        animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ========== 模块初始化 ==========

// 监听模块切换
document.addEventListener('DOMContentLoaded', () => {
    console.log('[企微机器人] DOMContentLoaded 事件触发');
    
    // 监听供应商通知群模块
    const supplierNav = document.querySelector('.nav-sub-item[data-module="supplier-notify"]');
    console.log('[企微机器人] 供应商导航元素:', supplierNav);
    
    if (supplierNav) {
        supplierNav.addEventListener('click', () => {
            console.log('[企微机器人] 点击了供应商通知群');
            setTimeout(() => {
                console.log('[企微机器人] 开始加载供应商数据');
                loadWebhooks('supplier');
                loadNotifications('supplier');
            }, 200);
        });
    }
    
    // 监听代理商通知群模块
    const agentNav = document.querySelector('.nav-sub-item[data-module="agent-notify"]');
    console.log('[企微机器人] 代理商导航元素:', agentNav);
    
    if (agentNav) {
        agentNav.addEventListener('click', () => {
            console.log('[企微机器人] 点击了代理商通知群');
            setTimeout(() => {
                console.log('[企微机器人] 开始加载代理商数据');
                loadWebhooks('agent');
                loadNotifications('agent');
            }, 200);
        });
    }
    
    // 如果当前模块是企微机器人，立即加载数据
    const currentModule = document.querySelector('.module-content.active');
    if (currentModule) {
        const moduleId = currentModule.id;
        console.log('[企微机器人] 当前激活模块:', moduleId);
        
        if (moduleId === 'supplier-notify-module') {
            console.log('[企微机器人] 当前在供应商通知群，立即加载数据');
            setTimeout(() => {
                loadWebhooks('supplier');
                loadNotifications('supplier');
            }, 300);
        } else if (moduleId === 'agent-notify-module') {
            console.log('[企微机器人] 当前在代理商通知群，立即加载数据');
            setTimeout(() => {
                loadWebhooks('agent');
                loadNotifications('agent');
            }, 300);
        }
    }
});

console.log('[企微机器人] DOMContentLoaded 监听器已注册');
console.log('[企微机器人] 准备进行全局导出...');
console.log('[企微机器人] showAddWebhookDialog 类型:', typeof showAddWebhookDialog);
console.log('[企微机器人] showCreateNotificationDialog 类型:', typeof showCreateNotificationDialog);

// ========== 全局导出 ==========
// 将关键函数导出到window对象，以便HTML中的onclick可以访问
try {
    console.log('[企微机器人] 开始导出函数到 window 对象...');
    
    window.showAddWebhookDialog = showAddWebhookDialog;
    console.log('[企微机器人] ✅ showAddWebhookDialog 已导出');
    
    window.showCreateNotificationDialog = showCreateNotificationDialog;
    console.log('[企微机器人] ✅ showCreateNotificationDialog 已导出');
    
    window.deleteWebhook = deleteWebhook;
    console.log('[企微机器人] ✅ deleteWebhook 已导出');
    
    window.editWebhook = editWebhook;
    console.log('[企微机器人] ✅ editWebhook 已导出');
    
    window.toggleWebhookStatus = toggleWebhookStatus;
    console.log('[企微机器人] ✅ toggleWebhookStatus 已导出');
    
    window.sendNotification = sendNotification;
    console.log('[企微机器人] ✅ sendNotification 已导出');
    
    window.loadWebhooks = loadWebhooks;
    console.log('[企微机器人] ✅ loadWebhooks 已导出');
    
    window.loadNotifications = loadNotifications;
    console.log('[企微机器人] ✅ loadNotifications 已导出');
    
    console.log('[企微机器人] 所有函数导出完成！');
    console.log('[企微机器人] 验证 window.showAddWebhookDialog:', typeof window.showAddWebhookDialog);
    
} catch (error) {
    console.error('[企微机器人] ❌ 导出函数时出错:', error);
    console.error('[企微机器人] 错误堆栈:', error.stack);
}

console.log('[企微机器人] 模块加载完成 v1.4 - 函数已导出到全局作用域');
console.log('[企微机器人] 已导出函数:', Object.keys(window).filter(k => k.includes('Webhook') || k.includes('Notification')));
