/**
 * 源数据管理模块
 * 支持灵活的数据源配置和数据推送
 */

console.log('[data-source.js] 开始加载...');

class DataSourceManager {
    constructor() {
        this.currentDataSources = [];
        this.currentSourceId = null;
    }

    /**
     * 初始化
     */
    async init() {
        await this.loadDataSources();
        this.bindEvents();
    }

    /**
     * 加载数据源列表
     */
    async loadDataSources() {
        console.log('[数据源] 开始加载数据源列表...');
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/data-source/list', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            console.log('[数据源] API 响应状态:', response.status);
            const result = await response.json();
            console.log('[数据源] API 返回结果:', result);
            
            if (result.code === 0) {
                this.currentDataSources = result.data;
                console.log('[数据源] 加载成功，数量:', result.data.length);
                this.renderDataSourceCards();
            } else {
                console.error('[数据源] 加载失败:', result.message);
            }
        } catch (error) {
            console.error('[数据源] 加载出错:', error);
        }
    }

    /**
     * 渲染数据源卡片
     */
    renderDataSourceCards() {
        const container = document.getElementById('dataSourceCards');
        if (!container) return;

        if (this.currentDataSources.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📦</div>
                    <div class="empty-text">还没有数据源</div>
                    <div class="empty-desc">点击"新建数据源"开始创建第一个数据源</div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.currentDataSources.map(source => this.renderDataSourceCard(source)).join('');
    }

    /**
     * 渲染单个数据源卡片
     */
    renderDataSourceCard(source) {
        const statusBadge = source.status === 'active' 
            ? '<span style="padding: 4px 12px; background: rgba(52, 199, 89, 0.12); color: #1B5E20; border-radius: 8px; font-size: 12px; font-weight: 500;"><i class="fas fa-check-circle"></i> 正常</span>'
            : '<span style="padding: 4px 12px; background: rgba(142, 142, 147, 0.12); color: #48484A; border-radius: 8px; font-size: 12px; font-weight: 500;"><i class="fas fa-pause-circle"></i> 已停用</span>';
        
        const typeMap = {
            'order': '📋 订单数据',
            'product': '📦 产品数据',
            'supplier': '🏢 供应商数据',
            'custom': '⚙️ 自定义数据'
        };
        
        const typeText = typeMap[source.source_type] || source.source_type;
        
        return `
            <div class="card" style="
                padding: 24px !important; 
                margin-bottom: 0 !important; 
                min-height: 320px; 
                display: flex; 
                flex-direction: column;
                background: white !important;
                border: 1px solid rgba(0, 0, 0, 0.1) !important;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08) !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 24px rgba(0, 0, 0, 0.12)'; this.style.borderColor='rgba(0, 122, 255, 0.3)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 12px rgba(0, 0, 0, 0.08)'; this.style.borderColor='rgba(0, 0, 0, 0.1)';" data-source-id="${source.id}">
                
                <!-- 头部：类型和状态 -->
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; gap: 12px;">
                    <div style="flex: 1; min-width: 0;">
                        <div style="padding: 6px 14px; background: rgba(0, 122, 255, 0.08); color: #007AFF; border-radius: 8px; font-size: 13px; font-weight: 500; display: inline-block; margin-bottom: 12px;">
                            ${typeText}
                        </div>
                        <h3 style="margin: 0; font-size: 19px; font-weight: 600; color: #1d1d1f; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            ${source.name}
                        </h3>
                    </div>
                    <div style="flex-shrink: 0;">${statusBadge}</div>
                </div>
                
                <!-- 描述 -->
                ${source.description ? `
                    <p style="margin: 0 0 16px 0; font-size: 14px; color: #86868B; line-height: 1.5; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                        ${source.description}
                    </p>
                ` : '<div style="height: 16px;"></div>'}
                
                <!-- 统计信息 -->
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; padding: 16px; background: #F5F5F7; border-radius: 10px; margin-bottom: 16px;">
                    <div style="text-align: center;">
                        <div style="font-size: 20px; font-weight: 600; color: #007AFF; margin-bottom: 4px;">
                            ${(source.total_records || 0).toLocaleString()}
                        </div>
                        <div style="font-size: 12px; color: #86868B;">总记录数</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 20px; font-weight: 600; color: #34C759; margin-bottom: 4px;">
                            ${source.sync_count || 0}
                        </div>
                        <div style="font-size: 12px; color: #86868B;">同步次数</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 13px; font-weight: 600; color: #636366; margin-bottom: 4px;">
                            ${source.last_sync_time ? this.formatTime(source.last_sync_time) : '未同步'}
                        </div>
                        <div style="font-size: 12px; color: #86868B;">最后同步</div>
                    </div>
                </div>
                
                <!-- 底部：操作按钮 -->
                <div style="margin-top: auto; display: flex; flex-wrap: wrap; gap: 8px;">
                    <button onclick="dataSourceManager.viewRecords('${source.id}')" style="
                        flex: 1;
                        min-width: 0;
                        padding: 8px 12px !important;
                        font-size: 13px !important;
                        background: rgba(0, 122, 255, 0.08) !important;
                        color: #007AFF !important;
                        border: 1px solid rgba(0, 122, 255, 0.2) !important;
                        border-radius: 8px !important;
                        font-weight: 500 !important;
                        cursor: pointer !important;
                        transition: all 0.2s !important;
                    " onmouseover="this.style.background='rgba(0, 122, 255, 0.15)'; this.style.borderColor='rgba(0, 122, 255, 0.4)';" onmouseout="this.style.background='rgba(0, 122, 255, 0.08)'; this.style.borderColor='rgba(0, 122, 255, 0.2)';">
                        <i class="fas fa-chart-bar"></i> 查看数据
                    </button>
                    <button onclick="dataSourceManager.showApiKeyDialog('${source.id}')" style="
                        flex: 1;
                        min-width: 0;
                        padding: 8px 12px !important;
                        font-size: 13px !important;
                        background: rgba(0, 122, 255, 0.08) !important;
                        color: #007AFF !important;
                        border: 1px solid rgba(0, 122, 255, 0.2) !important;
                        border-radius: 8px !important;
                        font-weight: 500 !important;
                        cursor: pointer !important;
                        transition: all 0.2s !important;
                    " onmouseover="this.style.background='rgba(0, 122, 255, 0.15)'; this.style.borderColor='rgba(0, 122, 255, 0.4)';" onmouseout="this.style.background='rgba(0, 122, 255, 0.08)'; this.style.borderColor='rgba(0, 122, 255, 0.2)';">
                        <i class="fas fa-key"></i> 密钥管理
                    </button>
                    <button onclick="dataSourceManager.showSyncDialog('${source.id}')" style="
                        flex: 1;
                        min-width: 0;
                        padding: 8px 12px !important;
                        font-size: 13px !important;
                        background: rgba(52, 199, 89, 0.08) !important;
                        color: #34C759 !important;
                        border: 1px solid rgba(52, 199, 89, 0.2) !important;
                        border-radius: 8px !important;
                        font-weight: 500 !important;
                        cursor: pointer !important;
                        transition: all 0.2s !important;
                    " onmouseover="this.style.background='rgba(52, 199, 89, 0.15)'; this.style.borderColor='rgba(52, 199, 89, 0.4)';" onmouseout="this.style.background='rgba(52, 199, 89, 0.08)'; this.style.borderColor='rgba(52, 199, 89, 0.2)';">
                        <i class="fas fa-sync-alt"></i> 手工同步
                    </button>
                    <button onclick="dataSourceManager.showEditDialog('${source.id}')" style="
                        flex: 1;
                        min-width: 0;
                        padding: 8px 12px !important;
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
                    <button onclick="dataSourceManager.confirmDelete('${source.id}', '${source.name}')" style="
                        flex: 1;
                        min-width: 0;
                        padding: 8px 12px !important;
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
        `;
    }

    /**
     * 格式化时间
     */
    formatTime(timeStr) {
        if (!timeStr) return '从未同步';
        
        const date = new Date(timeStr);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return '刚刚';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
        if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`;
        
        return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
    }
    
    /**
     * 格式化完整日期时间（用于详情页）
     * @param {string} timeStr - 时间字符串
     * @returns {string} - 格式化后的时间
     */
    formatDateTime(timeStr) {
        if (!timeStr) return '从未同步';
        
        try {
            const date = new Date(timeStr);
            
            // 检查日期是否有效
            if (isNaN(date.getTime())) {
                return '时间格式错误';
            }
            
            // 格式化为：2026-01-27 15:44:00
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');
            
            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
        } catch (error) {
            console.error('时间格式化错误:', error, timeStr);
            return '时间格式错误';
        }
    }

    /**
     * 显示新建数据源对话框
     */
    showCreateDialog() {
        const dialog = `
            <div class="modal-overlay" id="createSourceModal">
                <div class="modal-dialog modal-lg">
                    <div class="modal-header">
                        <h3>新建数据源</h3>
                        <button class="close-btn" onclick="closeModal('createSourceModal')">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="createSourceForm">
                            <div class="form-group">
                                <label>数据源名称 *</label>
                                <input type="text" name="name" class="form-control" placeholder="如：天号城订单源数据" required>
                            </div>
                            
                            <div class="form-group">
                                <label>数据源类型 *</label>
                                <select name="source_type" class="form-control" required>
                                    <option value="order">📋 订单数据</option>
                                    <option value="product">📦 产品数据</option>
                                    <option value="supplier">🏢 供应商数据</option>
                                    <option value="custom">⚙️ 自定义数据</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label>描述</label>
                                <textarea name="description" class="form-control" rows="3" placeholder="简要描述这个数据源的用途"></textarea>
                            </div>
                            
                            <div class="alert alert-info" style="margin: 16px 0; padding: 12px; background: var(--info-light); border: 1px solid var(--info-main); border-radius: var(--radius-sm); color: var(--grey-700);">
                                <div style="display: flex; gap: 8px; align-items: start;">
                                    <i class="fas fa-info-circle" style="color: var(--info-main); margin-top: 2px;"></i>
                                    <div>
                                        <strong>无需手动定义字段</strong>
                                        <p style="margin: 4px 0 0 0; font-size: 14px;">创建数据源后，直接导入 Excel 文件，系统会自动识别所有字段并保存。</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label class="checkbox-label">
                                    <input type="checkbox" name="auto_sync">
                                    启用自动同步
                                </label>
                            </div>
                            
                            <div class="form-group">
                                <label>同步间隔（秒）</label>
                                <input type="number" name="sync_interval" class="form-control" value="3600" min="60">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-outlined" onclick="closeModal('createSourceModal')">取消</button>
                        <button class="btn btn-primary" onclick="dataSourceManager.createDataSource()">创建</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', dialog);
    }

    /**
     * 创建数据源
     */
    async createDataSource() {
        const form = document.getElementById('createSourceForm');
        const formData = new FormData(form);
        
        try {
            // 使用空的字段定义（将在导入 Excel 时自动识别）
            const data = {
                name: formData.get('name'),
                source_type: formData.get('source_type'),
                description: formData.get('description') || '',
                field_schema: {"fields": []},  // 空字段定义
                auto_sync: formData.get('auto_sync') === 'on',
                sync_interval: parseInt(formData.get('sync_interval')) || 3600
            };
            
            const response = await fetch('/api/data-source/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.code === 0) {
                showToast('success', '数据源创建成功');
                closeModal('createSourceModal');
                
                // 显示API密钥
                this.showApiKeySuccess(result.data);
                
                // 刷新列表
                await this.loadDataSources();
            } else {
                showToast('error', result.message || '创建失败');
            }
        } catch (error) {
            console.error('创建数据源失败:', error);
            showToast('error', error.message || '创建失败');
        }
    }

    /**
     * 显示API密钥成功对话框
     */
    showApiKeySuccess(data) {
        const dialog = `
            <div class="modal-overlay" id="apiKeySuccessModal">
                <div class="modal-dialog">
                    <div class="modal-header">
                        <h3>🎉 数据源创建成功</h3>
                        <button class="close-btn" onclick="closeModal('apiKeySuccessModal')">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-success">
                            <strong>✓ 数据源已创建</strong>
                            <p>请将以下信息提供给技术团队：</p>
                        </div>
                        
                        <div class="api-key-info">
                            <div class="info-row">
                                <label>数据源ID:</label>
                                <div class="info-value">
                                    <code>${data.id}</code>
                                    <button class="btn-copy" onclick="copyText('${data.id}')">复制</button>
                                </div>
                            </div>
                            
                            <div class="info-row">
                                <label>API密钥:</label>
                                <div class="info-value">
                                    <code>${data.api_key}</code>
                                    <button class="btn-copy" onclick="copyText('${data.api_key}')">复制</button>
                                </div>
                            </div>
                            
                            <div class="info-row">
                                <label>推送地址:</label>
                                <div class="info-value">
                                    <code id="pushUrl">${window.location.origin}${data.push_url}</code>
                                    <button class="btn-copy" onclick="copyText(document.getElementById('pushUrl').textContent)">复制</button>
                                </div>
                            </div>
                            
                            <div class="alert alert-info" style="margin-top: 12px; padding: 10px; background: var(--info-light); border-left: 3px solid var(--info-main); font-size: 13px;">
                                <strong>📌 使用说明：</strong>
                                <p style="margin: 6px 0 0 0;">推送数据时需要在 <strong>HTTP Header</strong> 中携带 API 密钥：</p>
                                <code style="display: block; margin-top: 6px; padding: 8px; background: rgba(0,0,0,0.05); border-radius: 4px; font-size: 12px;">X-API-Key: ${data.api_key}</code>
                            </div>
                            
                            <div class="alert alert-warning" style="margin-top: 16px;">
                                <strong>⚠️ 注意</strong>
                                <p>当前显示的是本地地址 (${window.location.origin})。如果技术团队在外网，需要使用 <strong>ngrok</strong> 等内网穿透工具，或部署到公网服务器。</p>
                                <p style="margin-top: 8px; font-size: 12px; color: #637381;">
                                    <a href="#" onclick="alert('1. 下载 ngrok: https://ngrok.com/\\n2. 运行: ngrok http 9999\\n3. 使用 ngrok 提供的公网地址'); return false;" style="color: #FF6B1A;">查看如何配置 →</a>
                                </p>
                            </div>
                        </div>
                        
                        <div class="alert alert-warning">
                            <strong>⚠️ 重要提示</strong>
                            <p>请妥善保管API密钥，关闭此对话框后将无法再次查看完整密钥。</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-primary" onclick="closeModal('apiKeySuccessModal')">我已保存</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', dialog);
    }

    /**
     * 显示API密钥管理对话框
     */
    async showApiKeyDialog(sourceId) {
        const source = this.currentDataSources.find(s => s.id === sourceId);
        if (!source) return;
        
        const dialog = `
            <div style="
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0, 0, 0, 0.4);
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                animation: fadeIn 0.2s;
            " id="apiKeyModal" onclick="if(event.target===this) closeModal('apiKeyModal')">
                <div style="
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 24px 48px rgba(0, 0, 0, 0.24);
                    width: 90%;
                    max-width: 750px;
                    max-height: 90vh;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                " onclick="event.stopPropagation()">
                    
                    <!-- 头部 -->
                    <div style="padding: 24px 28px; border-bottom: 1px solid rgba(0, 0, 0, 0.08); display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; font-size: 20px; font-weight: 600; color: #1d1d1f;">
                            <i class="fas fa-key" style="color: #007AFF; margin-right: 8px;"></i>
                            API密钥管理
                        </h3>
                        <button onclick="closeModal('apiKeyModal')" style="
                            width: 32px; height: 32px;
                            border: none;
                            background: rgba(0, 0, 0, 0.06);
                            border-radius: 50%;
                            font-size: 20px;
                            color: #636366;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            transition: all 0.2s;
                        " onmouseover="this.style.background='rgba(0, 0, 0, 0.1)'" onmouseout="this.style.background='rgba(0, 0, 0, 0.06)'">
                            ×
                        </button>
                    </div>
                    
                    <!-- 内容区域 -->
                    <div style="padding: 24px 28px; overflow-y: auto; flex: 1;">
                        
                        <!-- 数据源信息 -->
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #636366; margin-bottom: 8px;">数据源</label>
                            <div style="padding: 12px 16px; background: #F5F5F7; border-radius: 10px; font-size: 15px; color: #1d1d1f; font-weight: 500;">${source.name}</div>
                        </div>
                        
                        <!-- 数据源ID -->
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #636366; margin-bottom: 8px;">数据源ID</label>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <code style="flex: 1; padding: 12px 16px; background: #F5F5F7; border-radius: 10px; font-size: 13px; color: #636366; font-family: 'SF Mono', Monaco, monospace; overflow: hidden; text-overflow: ellipsis;">${source.id}</code>
                                <button onclick="copyText('${source.id}')" style="
                                    padding: 8px 16px;
                                    background: rgba(0, 122, 255, 0.08);
                                    color: #007AFF;
                                    border: 1px solid rgba(0, 122, 255, 0.2);
                                    border-radius: 8px;
                                    font-size: 13px;
                                    font-weight: 500;
                                    cursor: pointer;
                                    transition: all 0.2s;
                                    white-space: nowrap;
                                " onmouseover="this.style.background='rgba(0, 122, 255, 0.15)'; this.style.borderColor='rgba(0, 122, 255, 0.4)'" onmouseout="this.style.background='rgba(0, 122, 255, 0.08)'; this.style.borderColor='rgba(0, 122, 255, 0.2)'">
                                    <i class="fas fa-copy"></i> 复制
                                </button>
                            </div>
                        </div>
                        
                        <!-- API密钥 -->
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #636366; margin-bottom: 8px;">API密钥</label>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <code style="flex: 1; padding: 12px 16px; background: #F5F5F7; border-radius: 10px; font-size: 13px; color: #636366; font-family: 'SF Mono', Monaco, monospace; overflow: hidden; text-overflow: ellipsis;">${source.api_key}</code>
                                <button onclick="copyText('${source.api_key}')" style="
                                    padding: 8px 16px;
                                    background: rgba(0, 122, 255, 0.08);
                                    color: #007AFF;
                                    border: 1px solid rgba(0, 122, 255, 0.2);
                                    border-radius: 8px;
                                    font-size: 13px;
                                    font-weight: 500;
                                    cursor: pointer;
                                    transition: all 0.2s;
                                    white-space: nowrap;
                                " onmouseover="this.style.background='rgba(0, 122, 255, 0.15)'; this.style.borderColor='rgba(0, 122, 255, 0.4)'" onmouseout="this.style.background='rgba(0, 122, 255, 0.08)'; this.style.borderColor='rgba(0, 122, 255, 0.2)'">
                                    <i class="fas fa-copy"></i> 复制
                                </button>
                            </div>
                        </div>
                        
                        <!-- 推送地址 -->
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #636366; margin-bottom: 8px;">推送地址</label>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <code id="pushUrlInModal" style="flex: 1; padding: 12px 16px; background: #F5F5F7; border-radius: 10px; font-size: 13px; color: #636366; font-family: 'SF Mono', Monaco, monospace; overflow: hidden; text-overflow: ellipsis;">${window.location.origin}/api/data-source/push</code>
                                <button onclick="copyText(document.getElementById('pushUrlInModal').textContent)" style="
                                    padding: 8px 16px;
                                    background: rgba(0, 122, 255, 0.08);
                                    color: #007AFF;
                                    border: 1px solid rgba(0, 122, 255, 0.2);
                                    border-radius: 8px;
                                    font-size: 13px;
                                    font-weight: 500;
                                    cursor: pointer;
                                    transition: all 0.2s;
                                    white-space: nowrap;
                                " onmouseover="this.style.background='rgba(0, 122, 255, 0.15)'; this.style.borderColor='rgba(0, 122, 255, 0.4)'" onmouseout="this.style.background='rgba(0, 122, 255, 0.08)'; this.style.borderColor='rgba(0, 122, 255, 0.2)'">
                                    <i class="fas fa-copy"></i> 复制
                                </button>
                            </div>
                        </div>
                        
                        <!-- 查询地址 -->
                        <div style="margin-bottom: 24px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #636366; margin-bottom: 8px;">查询地址</label>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <code id="queryUrlInModal" style="flex: 1; padding: 12px 16px; background: #F5F5F7; border-radius: 10px; font-size: 13px; color: #636366; font-family: 'SF Mono', Monaco, monospace; overflow: hidden; text-overflow: ellipsis;">${window.location.origin}/api/data-source/${source.id}/query</code>
                                <button onclick="copyText(document.getElementById('queryUrlInModal').textContent)" style="
                                    padding: 8px 16px;
                                    background: rgba(0, 122, 255, 0.08);
                                    color: #007AFF;
                                    border: 1px solid rgba(0, 122, 255, 0.2);
                                    border-radius: 8px;
                                    font-size: 13px;
                                    font-weight: 500;
                                    cursor: pointer;
                                    transition: all 0.2s;
                                    white-space: nowrap;
                                " onmouseover="this.style.background='rgba(0, 122, 255, 0.15)'; this.style.borderColor='rgba(0, 122, 255, 0.4)'" onmouseout="this.style.background='rgba(0, 122, 255, 0.08)'; this.style.borderColor='rgba(0, 122, 255, 0.2)'">
                                    <i class="fas fa-copy"></i> 复制
                                </button>
                            </div>
                        </div>
                        
                        <!-- 推送数据说明 -->
                        <div style="margin-bottom: 16px; padding: 16px; background: rgba(0, 122, 255, 0.08); border-left: 3px solid #007AFF; border-radius: 10px;">
                            <div style="font-size: 14px; font-weight: 600; color: #1d1d1f; margin-bottom: 8px;">
                                <i class="fas fa-arrow-right" style="color: #007AFF;"></i> 推送数据（技术团队→系统）
                            </div>
                            <p style="margin: 0 0 10px 0; font-size: 13px; color: #636366; line-height: 1.6;">
                                使用推送地址，在 <strong>Header</strong> 中携带 API 密钥：
                            </p>
                            <code style="display: block; padding: 12px; background: rgba(0, 0, 0, 0.05); border-radius: 8px; font-size: 12px; color: #636366; font-family: 'SF Mono', Monaco, monospace; line-height: 1.6;">
POST ${window.location.origin}/api/data-source/push<br>
Header: X-API-Key: ${source.api_key}
                            </code>
                        </div>
                        
                        <!-- 查询数据说明 -->
                        <div style="margin-bottom: 16px; padding: 16px; background: rgba(52, 199, 89, 0.08); border-left: 3px solid #34C759; border-radius: 10px;">
                            <div style="font-size: 14px; font-weight: 600; color: #1d1d1f; margin-bottom: 8px;">
                                <i class="fas fa-arrow-left" style="color: #34C759;"></i> 查询数据（系统→技术团队）
                            </div>
                            <p style="margin: 0 0 10px 0; font-size: 13px; color: #636366; line-height: 1.6;">
                                使用查询地址，在 <strong>Header</strong> 中携带 API 密钥：
                            </p>
                            <code style="display: block; padding: 12px; background: rgba(0, 0, 0, 0.05); border-radius: 8px; font-size: 12px; color: #636366; font-family: 'SF Mono', Monaco, monospace; line-height: 1.6;">
GET ${window.location.origin}/api/data-source/${source.id}/query?limit=1<br>
Header: X-API-Key: ${source.api_key}
                            </code>
                        </div>
                        
                        <!-- 网络访问提示 -->
                        <div style="margin-bottom: 16px; padding: 16px; background: rgba(255, 149, 0, 0.08); border-left: 3px solid #FF9500; border-radius: 10px;">
                            <div style="font-size: 14px; font-weight: 600; color: #1d1d1f; margin-bottom: 8px;">
                                <i class="fas fa-exclamation-circle" style="color: #FF9500;"></i> 网络访问提示
                            </div>
                            <p style="margin: 0 0 10px 0; font-size: 13px; color: #636366; line-height: 1.6;">
                                当前地址为本地地址，外网无法访问。
                            </p>
                            <div style="font-size: 13px; font-weight: 600; color: #636366; margin-bottom: 6px;">解决方案：</div>
                            <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #636366; line-height: 1.8;">
                                <li><strong>方案1：</strong> 使用 ngrok 内网穿透<br>
                                    <code style="background: rgba(255,149,0,0.1); padding: 2px 6px; border-radius: 4px; font-size: 12px;">ngrok http 9999</code>
                                </li>
                                <li><strong>方案2：</strong> 部署到有公网IP的服务器</li>
                                <li><strong>方案3：</strong> 让技术团队导出Excel，手工导入</li>
                            </ul>
                        </div>
                        
                        <!-- 安全提示 -->
                        <div style="padding: 16px; background: rgba(255, 59, 48, 0.08); border-left: 3px solid #FF3B30; border-radius: 10px;">
                            <div style="font-size: 14px; font-weight: 600; color: #1d1d1f; margin-bottom: 8px;">
                                <i class="fas fa-shield-alt" style="color: #FF3B30;"></i> 安全提示
                            </div>
                            <p style="margin: 0; font-size: 13px; color: #636366; line-height: 1.6;">
                                重新生成密钥后，旧密钥将立即失效，请及时更新技术团队的配置。
                            </p>
                        </div>
                    </div>
                    
                    <!-- 底部按钮区 -->
                    <div style="padding: 20px 28px; border-top: 1px solid rgba(0, 0, 0, 0.08); background: #F5F5F7; display: flex; justify-content: flex-end; gap: 12px;">
                        <button onclick="closeModal('apiKeyModal')" style="
                            padding: 10px 24px;
                            background: rgba(0, 0, 0, 0.06);
                            color: #1d1d1f;
                            border: none;
                            border-radius: 10px;
                            font-size: 15px;
                            font-weight: 500;
                            cursor: pointer;
                            transition: all 0.2s;
                        " onmouseover="this.style.background='rgba(0, 0, 0, 0.1)'" onmouseout="this.style.background='rgba(0, 0, 0, 0.06)'">
                            关闭
                        </button>
                        <button onclick="dataSourceManager.regenerateApiKey('${sourceId}')" style="
                            padding: 10px 24px;
                            background: rgba(255, 149, 0, 0.08);
                            color: #FF9500;
                            border: 1px solid rgba(255, 149, 0, 0.2);
                            border-radius: 10px;
                            font-size: 15px;
                            font-weight: 500;
                            cursor: pointer;
                            transition: all 0.2s;
                        " onmouseover="this.style.background='rgba(255, 149, 0, 0.15)'; this.style.borderColor='rgba(255, 149, 0, 0.4)'" onmouseout="this.style.background='rgba(255, 149, 0, 0.08)'; this.style.borderColor='rgba(255, 149, 0, 0.2)'">
                            <i class="fas fa-sync-alt"></i> 重新生成
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', dialog);
    }

    /**
     * 重新生成API密钥
     */
    async regenerateApiKey(sourceId) {
        if (!confirm('确定要重新生成API密钥吗？旧密钥将立即失效。')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/data-source/${sourceId}/regenerate-key`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            
            if (result.code === 0) {
                showToast('success', '密钥已重新生成');
                closeModal('apiKeyModal');
                await this.loadDataSources();
                
                // 重新显示对话框
                setTimeout(() => this.showApiKeyDialog(sourceId), 300);
            } else {
                showToast('error', result.message || '操作失败');
            }
        } catch (error) {
            console.error('重新生成密钥失败:', error);
            showToast('error', '操作失败');
        }
    }

    /**
     * 查看数据记录
     */
    viewRecords(sourceId) {
        this.currentSourceId = sourceId;
        // 切换到数据查看页面
        window.location.hash = '#data-records';
        this.loadRecords(sourceId);
    }

    /**
     * 加载数据记录
     */
    async loadRecords(sourceId, page = 1) {
        // 这部分功能将在下一步实现
        showToast('info', '数据查看功能开发中...');
    }

    /**
     * 显示手工同步对话框
     */
    showSyncDialog(sourceId) {
        // 手工同步功能将在数据导入模块实现
        showToast('info', '手工同步功能开发中...');
    }

    /**
     * 显示编辑对话框
     */
    showEditDialog(sourceId) {
        const source = this.currentDataSources.find(s => s.id === sourceId);
        if (!source) return;
        
        const dialog = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                animation: fadeIn 0.2s;
            " id="editSourceModal" onclick="if(event.target===this) closeModal('editSourceModal')">
                <div style="
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 24px 48px rgba(0, 0, 0, 0.24);
                    width: 90%;
                    max-width: 540px;
                    max-height: 90vh;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                " onclick="event.stopPropagation()">
                    
                    <!-- 头部 -->
                    <div style="padding: 24px 28px; border-bottom: 1px solid rgba(0, 0, 0, 0.08);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; font-size: 20px; font-weight: 600; color: #1d1d1f;">
                                <i class="fas fa-edit" style="color: #007AFF; margin-right: 8px;"></i>
                                编辑数据源
                            </h3>
                            <button onclick="closeModal('editSourceModal')" style="
                                width: 32px;
                                height: 32px;
                                border: none;
                                background: rgba(0, 0, 0, 0.06);
                                border-radius: 50%;
                                font-size: 20px;
                                color: #636366;
                                cursor: pointer;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                transition: all 0.2s;
                            " onmouseover="this.style.background='rgba(0, 0, 0, 0.1)'" onmouseout="this.style.background='rgba(0, 0, 0, 0.06)'">
                                ×
                            </button>
                        </div>
                    </div>
                    
                    <!-- 内容区域 -->
                    <div style="padding: 24px 28px; overflow-y: auto; flex: 1;">
                        <form id="editSourceForm">
                            <input type="hidden" name="source_id" value="${source.id}">
                            
                            <!-- 数据源名称 -->
                            <div style="margin-bottom: 20px;">
                                <label style="display: block; font-size: 13px; font-weight: 600; color: #636366; margin-bottom: 8px;">
                                    数据源名称 <span style="color: #FF3B30;">*</span>
                                </label>
                                <input type="text" name="name" value="${source.name}" required style="
                                    width: 100%;
                                    padding: 12px 16px;
                                    border: 1px solid rgba(0, 0, 0, 0.12);
                                    border-radius: 10px;
                                    font-size: 15px;
                                    color: #1d1d1f;
                                    outline: none;
                                    transition: all 0.2s;
                                    box-sizing: border-box;
                                " onfocus="this.style.borderColor='#007AFF'; this.style.boxShadow='0 0 0 4px rgba(0,122,255,0.1)'" onblur="this.style.borderColor='rgba(0,0,0,0.12)'; this.style.boxShadow='none'">
                            </div>
                            
                            <!-- 描述 -->
                            <div style="margin-bottom: 20px;">
                                <label style="display: block; font-size: 13px; font-weight: 600; color: #636366; margin-bottom: 8px;">
                                    描述
                                </label>
                                <textarea name="description" rows="3" style="
                                    width: 100%;
                                    padding: 12px 16px;
                                    border: 1px solid rgba(0, 0, 0, 0.12);
                                    border-radius: 10px;
                                    font-size: 15px;
                                    color: #1d1d1f;
                                    outline: none;
                                    transition: all 0.2s;
                                    resize: vertical;
                                    min-height: 100px;
                                    box-sizing: border-box;
                                    font-family: inherit;
                                " onfocus="this.style.borderColor='#007AFF'; this.style.boxShadow='0 0 0 4px rgba(0,122,255,0.1)'" onblur="this.style.borderColor='rgba(0,0,0,0.12)'; this.style.boxShadow='none'">${source.description || ''}</textarea>
                            </div>
                            
                            <!-- 状态 -->
                            <div style="margin-bottom: 20px;">
                                <label style="display: block; font-size: 13px; font-weight: 600; color: #636366; margin-bottom: 8px;">
                                    状态
                                </label>
                                <select name="status" style="
                                    width: 100%;
                                    padding: 12px 16px;
                                    border: 1px solid rgba(0, 0, 0, 0.12);
                                    border-radius: 10px;
                                    font-size: 15px;
                                    color: #1d1d1f;
                                    outline: none;
                                    transition: all 0.2s;
                                    background: white;
                                    cursor: pointer;
                                    box-sizing: border-box;
                                " onfocus="this.style.borderColor='#007AFF'; this.style.boxShadow='0 0 0 4px rgba(0,122,255,0.1)'" onblur="this.style.borderColor='rgba(0,0,0,0.12)'; this.style.boxShadow='none'">
                                    <option value="active" ${source.status === 'active' ? 'selected' : ''}>正常</option>
                                    <option value="inactive" ${source.status === 'inactive' ? 'selected' : ''}>已停用</option>
                                </select>
                            </div>
                            
                            <!-- 自动同步 -->
                            <div style="margin-bottom: 20px;">
                                <label style="display: flex; align-items: center; cursor: pointer; user-select: none;">
                                    <input type="checkbox" name="auto_sync" ${source.auto_sync ? 'checked' : ''} style="
                                        width: 20px;
                                        height: 20px;
                                        margin-right: 10px;
                                        cursor: pointer;
                                        accent-color: #007AFF;
                                    ">
                                    <span style="font-size: 15px; color: #1d1d1f; font-weight: 500;">启用自动同步</span>
                                </label>
                            </div>
                            
                            <!-- 同步间隔 -->
                            <div style="margin-bottom: 20px;">
                                <label style="display: block; font-size: 13px; font-weight: 600; color: #636366; margin-bottom: 8px;">
                                    同步间隔（秒）
                                </label>
                                <input type="number" name="sync_interval" value="${source.sync_interval || 3600}" min="60" style="
                                    width: 100%;
                                    padding: 12px 16px;
                                    border: 1px solid rgba(0, 0, 0, 0.12);
                                    border-radius: 10px;
                                    font-size: 15px;
                                    color: #1d1d1f;
                                    outline: none;
                                    transition: all 0.2s;
                                    box-sizing: border-box;
                                " onfocus="this.style.borderColor='#007AFF'; this.style.boxShadow='0 0 0 4px rgba(0,122,255,0.1)'" onblur="this.style.borderColor='rgba(0,0,0,0.12)'; this.style.boxShadow='none'">
                            </div>
                            
                            <!-- 提示信息 -->
                            <div style="padding: 16px; background: rgba(255, 149, 0, 0.08); border-left: 3px solid #FF9500; border-radius: 10px;">
                                <div style="font-size: 14px; font-weight: 600; color: #1d1d1f; margin-bottom: 8px;">
                                    <i class="fas fa-exclamation-circle" style="color: #FF9500;"></i> 注意
                                </div>
                                <p style="margin: 0; font-size: 13px; color: #636366; line-height: 1.6;">
                                    字段定义暂不支持修改，如需修改请联系管理员。
                                </p>
                            </div>
                        </form>
                    </div>
                    
                    <!-- 底部按钮区 -->
                    <div style="padding: 20px 28px; border-top: 1px solid rgba(0, 0, 0, 0.08); background: #F5F5F7; display: flex; justify-content: flex-end; gap: 12px;">
                        <button onclick="closeModal('editSourceModal')" style="
                            padding: 10px 24px;
                            background: rgba(0, 0, 0, 0.06);
                            color: #1d1d1f;
                            border: none;
                            border-radius: 10px;
                            font-size: 15px;
                            font-weight: 500;
                            cursor: pointer;
                            transition: all 0.2s;
                        " onmouseover="this.style.background='rgba(0, 0, 0, 0.1)'" onmouseout="this.style.background='rgba(0, 0, 0, 0.06)'">
                            取消
                        </button>
                        <button onclick="dataSourceManager.updateDataSource()" style="
                            padding: 10px 24px;
                            background: linear-gradient(135deg, #007AFF 0%, #0051D5 100%);
                            color: white;
                            border: none;
                            border-radius: 10px;
                            font-size: 15px;
                            font-weight: 600;
                            cursor: pointer;
                            transition: all 0.2s;
                            box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3);
                        " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(0, 122, 255, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0, 122, 255, 0.3)'">
                            <i class="fas fa-save"></i> 保存
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', dialog);
    }
    
    /**
     * 更新数据源
     */
    async updateDataSource() {
        const form = document.getElementById('editSourceForm');
        const formData = new FormData(form);
        const sourceId = formData.get('source_id');
        
        try {
            const data = {
                name: formData.get('name'),
                description: formData.get('description'),
                status: formData.get('status'),
                auto_sync: formData.get('auto_sync') === 'on',
                sync_interval: parseInt(formData.get('sync_interval'))
            };
            
            const response = await fetch(`/api/data-source/${sourceId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.code === 0) {
                showToast('success', '更新成功');
                closeModal('editSourceModal');
                await this.loadDataSources();
            } else {
                showToast('error', result.message || '更新失败');
            }
        } catch (error) {
            console.error('更新数据源失败:', error);
            showToast('error', '更新失败');
        }
    }
    
    /**
     * 确认删除
     */
    confirmDelete(sourceId, sourceName) {
        const dialog = `
            <div class="modal-overlay" id="deleteConfirmModal">
                <div class="modal-dialog">
                    <div class="modal-header">
                        <h3>⚠️ 确认删除</h3>
                        <button class="close-btn" onclick="closeModal('deleteConfirmModal')">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-warning">
                            <strong>警告</strong>
                            <p>你确定要删除数据源 <strong>"${sourceName}"</strong> 吗？</p>
                        </div>
                        <p style="margin-top: 16px; color: #637381;">此操作将：</p>
                        <ul style="margin: 8px 0 0 20px; color: #637381; line-height: 1.8;">
                            <li>停用数据源</li>
                            <li>API密钥失效</li>
                            <li>停止接收新数据</li>
                            <li><strong style="color: #FF5630;">不会删除已有数据</strong></li>
                        </ul>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-outlined" onclick="closeModal('deleteConfirmModal')">取消</button>
                        <button class="btn btn-danger" onclick="dataSourceManager.deleteDataSource('${sourceId}')">确认删除</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', dialog);
    }
    
    /**
     * 删除数据源
     */
    async deleteDataSource(sourceId) {
        try {
            const response = await fetch(`/api/data-source/${sourceId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const result = await response.json();
            
            if (result.code === 0) {
                showToast('success', '删除成功');
                closeModal('deleteConfirmModal');
                await this.loadDataSources();
            } else {
                showToast('error', result.message || '删除失败');
            }
        } catch (error) {
            console.error('删除数据源失败:', error);
            showToast('error', '删除失败');
        }
    }

    /**
     * 显示配置对话框
     */
    showConfigDialog(sourceId) {
        const source = this.currentDataSources.find(s => s.id === sourceId);
        if (!source) return;
        
        showToast('info', '配置功能开发中...');
    }

    /**
     * 查看数据源的数据记录
     */
    async viewRecords(sourceId) {
        console.log('[查看数据] sourceId:', sourceId);
        
        // 获取数据源信息
        const source = this.currentDataSources.find(s => s.id === sourceId);
        if (!source) {
            alert('数据源不存在');
            return;
        }
        
        // 保存当前数据源信息
        this.currentSourceId = sourceId;
        this.currentSource = source;
        this.currentPage = 1;
        this.currentSearch = '';
        
        // 切换到详情页面
        switchModule('data-source-detail');
        
        // 更新页面信息
        document.getElementById('detailSourceName').textContent = source.name;
        document.getElementById('detailTotalRecords').textContent = (source.total_records || 0).toLocaleString();
        document.getElementById('detailSyncCount').textContent = (source.sync_count || 0).toLocaleString();
        document.getElementById('detailLastSync').textContent = this.formatDateTime(source.last_sync_time);
        
        // 加载数据记录
        await this.loadRecords();
    }
    
    /**
     * 加载数据记录
     */
    async loadRecords() {
        try {
            const url = `/api/data-source/${this.currentSourceId}/records?page=${this.currentPage}&limit=20${this.currentSearch ? `&search=${encodeURIComponent(this.currentSearch)}` : ''}`;
            console.log('[加载记录] URL:', url);
            
            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const result = await response.json();
            
            console.log('[加载记录] 结果:', result);
            
            if (result.code === 0) {
                this.renderRecordsTable(result.data, this.currentSource);
                this.renderPagination(result.total, result.page, result.limit);
                
                // 更新最新订单时间
                this.updateLatestOrderTime(result.data);
            } else {
                showToast(result.message || '加载失败', 'error');
            }
        } catch (error) {
            console.error('[加载记录] 错误:', error);
            showToast('加载失败', 'error');
        }
    }
    
    /**
     * 渲染数据表格
     */
    renderRecordsTable(records, source) {
        const thead = document.getElementById('recordsTableHead');
        const tbody = document.getElementById('recordsTableBody');
        
        if (!records || records.length === 0) {
            thead.innerHTML = '';
            tbody.innerHTML = `
                <tr>
                    <td colspan="100" class="empty-table">
                        <i class="fas fa-inbox"></i>
                        <p>暂无数据记录</p>
                        <small>点击"导入 Excel"或"添加记录"开始添加数据</small>
                    </td>
                </tr>
            `;
            return;
        }
        
        // 解析字段定义
        let fieldSchema = [];
        try {
            fieldSchema = source.field_schema ? (typeof source.field_schema === 'string' ? JSON.parse(source.field_schema) : source.field_schema) : [];
        } catch (e) {
            console.error('字段定义解析失败:', e);
        }
        
        // 生成表头
        const headers = ['ID', '数据键'];
        const fieldNames = [];
        
        if (fieldSchema.fields && Array.isArray(fieldSchema.fields)) {
            fieldSchema.fields.forEach(field => {
                headers.push(field.name || field.field_name);
                fieldNames.push(field.field_name || field.name);
            });
        } else if (records[0] && records[0].raw_data) {
            // 从第一条记录提取字段
            Object.keys(records[0].raw_data).forEach(key => {
                headers.push(key);
                fieldNames.push(key);
            });
        }
        
        headers.push('创建时间', '操作');
        
        thead.innerHTML = `
            <tr>
                ${headers.map(h => `<th>${h}</th>`).join('')}
            </tr>
        `;
        
        // 生成表格内容
        tbody.innerHTML = records.map(record => {
            const data = record.raw_data || {};
            const cells = [
                record.id.substring(0, 8),
                record.data_key || '-'
            ];
            
            // 添加字段值
            fieldNames.forEach(fieldName => {
                const value = data[fieldName];
                cells.push(value !== undefined && value !== null ? value : '-');
            });
            
            // 添加创建时间
            const createTime = new Date(record.created_at).toLocaleString('zh-CN');
            cells.push(createTime);
            
            // 操作按钮
            cells.push(`
                <div class="actions">
                    <button class="btn btn-sm btn-outlined" onclick="dataSourceManager.editRecord('${record.id}')">编辑</button>
                    <button class="btn btn-sm btn-danger" onclick="dataSourceManager.deleteRecord('${record.id}')">删除</button>
                </div>
            `);
            
            return `<tr>${cells.map(c => `<td>${c}</td>`).join('')}</tr>`;
        }).join('');
        
        // 检测表格是否需要滚动
        setTimeout(() => {
            const container = document.querySelector('.data-table-container');
            if (container && container.scrollWidth > container.clientWidth) {
                container.classList.add('has-scroll');
                // 3秒后移除提示
                setTimeout(() => {
                    container.classList.remove('has-scroll');
                }, 3000);
            }
        }, 100);
    }
    
    /**
     * 更新最新订单时间
     */
    updateLatestOrderTime(records) {
        const latestOrderEl = document.getElementById('detailLatestOrder');
        
        if (!latestOrderEl) {
            console.warn('最新订单元素未找到');
            return;
        }
        
        if (!records || records.length === 0) {
            latestOrderEl.textContent = '暂无订单';
            return;
        }
        
        // 从所有记录中找出最新的创建时间
        let latestTime = null;
        
        for (const record of records) {
            // 尝试多个可能的时间字段
            const timeStr = record.created_at || record.createTime || record.create_time;
            
            if (timeStr) {
                const time = new Date(timeStr);
                if (!isNaN(time.getTime())) {
                    if (!latestTime || time > latestTime) {
                        latestTime = time;
                    }
                }
            }
        }
        
        if (latestTime) {
            latestOrderEl.textContent = this.formatDateTime(latestTime.toISOString());
        } else {
            latestOrderEl.textContent = '暂无订单';
        }
    }
    
    /**
     * 渲染分页
     */
    renderPagination(total, page, limit) {
        const totalPages = Math.ceil(total / limit);
        const paginationEl = document.getElementById('recordsPagination');
        
        if (totalPages <= 1) {
            paginationEl.innerHTML = '';
            return;
        }
        
        let html = '';
        
        // 上一页
        html += `<button class="pagination-item" ${page <= 1 ? 'disabled' : ''} onclick="dataSourceManager.goToPage(${page - 1})">上一页</button>`;
        
        // 页码
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= page - 2 && i <= page + 2)) {
                html += `<button class="pagination-item ${i === page ? 'active' : ''}" onclick="dataSourceManager.goToPage(${i})">${i}</button>`;
            } else if (i === page - 3 || i === page + 3) {
                html += `<span class="pagination-item">...</span>`;
            }
        }
        
        // 下一页
        html += `<button class="pagination-item" ${page >= totalPages ? 'disabled' : ''} onclick="dataSourceManager.goToPage(${page + 1})">下一页</button>`;
        
        paginationEl.innerHTML = html;
    }
    
    /**
     * 跳转页码
     */
    goToPage(page) {
        this.currentPage = page;
        this.loadRecords();
    }
    
    /**
     * 搜索记录
     */
    searchRecords() {
        const searchInput = document.getElementById('recordSearch');
        this.currentSearch = searchInput ? searchInput.value : '';
        this.currentPage = 1;
        this.loadRecords();
    }
    
    /**
     * 刷新记录
     */
    refreshRecords() {
        this.loadRecords();
        showToast('已刷新', 'success');
    }
    
    /**
     * 返回列表
     */
    backToList() {
        switchModule('data-sources-internal');
        this.loadDataSources();
    }
    
    /**
     * 显示导入对话框
     */
    showImportDialog() {
        const modal = document.getElementById('importExcelModal');
        if (modal) {
            modal.style.display = 'flex';
            
            // 重置表单
            document.getElementById('excelFileInput').value = '';
            document.getElementById('importIncremental').checked = false;
            document.getElementById('importPreview').style.display = 'none';
            document.getElementById('importProgress').style.display = 'none';
            
            // 绑定文件选择事件
            const fileInput = document.getElementById('excelFileInput');
            fileInput.onchange = (e) => this.previewFile(e);
        }
    }
    
    /**
     * 关闭导入对话框
     */
    closeImportDialog() {
        const modal = document.getElementById('importExcelModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    /**
     * 预览文件
     */
    previewFile(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // 显示预览信息
        document.getElementById('previewFileName').textContent = file.name;
        document.getElementById('previewFileSize').textContent = this.formatFileSize(file.size);
        document.getElementById('importPreview').style.display = 'block';
    }
    
    /**
     * 格式化文件大小
     */
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    }
    
    /**
     * 开始导入
     */
    async startImport() {
        const fileInput = document.getElementById('excelFileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            showToast('请选择文件', 'error');
            return;
        }
        
        // 检查文件类型
        if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
            showToast('只支持 .xlsx 和 .xls 格式', 'error');
            return;
        }
        
        const incremental = document.getElementById('importIncremental').checked;
        
        // 显示进度
        document.getElementById('importProgress').style.display = 'block';
        document.getElementById('importProgressText').textContent = '正在上传...';
        document.getElementById('importProgressFill').style.width = '30%';
        document.getElementById('btnStartImport').disabled = true;
        
        try {
            // 创建 FormData
            const formData = new FormData();
            formData.append('file', file);
            
            const url = `/api/data-source/${this.currentSourceId}/import-excel?incremental=${incremental}`;
            
            console.log('[导入] 开始上传:', url);
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: formData
            });
            
            document.getElementById('importProgressText').textContent = '正在处理...';
            document.getElementById('importProgressFill').style.width = '60%';
            
            const result = await response.json();
            
            console.log('[导入] 结果:', result);
            
            document.getElementById('importProgressFill').style.width = '100%';
            
            if (result.code === 0) {
                document.getElementById('importProgressText').textContent = '导入成功！';
                showToast(result.message, 'success');
                
                // 延迟关闭对话框并刷新数据
                setTimeout(() => {
                    this.closeImportDialog();
                    this.refreshRecords();
                    // 重新加载数据源列表以更新统计
                    this.loadDataSources();
                }, 1500);
            } else {
                document.getElementById('importProgressText').textContent = '导入失败';
                document.getElementById('importProgressFill').style.width = '0';
                showToast(result.message || '导入失败', 'error');
                document.getElementById('btnStartImport').disabled = false;
            }
        } catch (error) {
            console.error('[导入] 错误:', error);
            document.getElementById('importProgressText').textContent = '导入失败';
            document.getElementById('importProgressFill').style.width = '0';
            showToast('导入失败：' + error.message, 'error');
            document.getElementById('btnStartImport').disabled = false;
        }
    }

    /**
     * 显示导入对话框（待实现）
     */
    showImportDialog_OLD() {
        showToast('Excel 导入功能开发中...', 'info');
    }
    
    /**
     * 显示添加记录对话框（待实现）
     */
    showAddRecordDialog() {
        showToast('添加记录功能开发中...', 'info');
    }
    
    /**
     * 编辑记录（待实现）
     */
    editRecord(recordId) {
        showToast('编辑功能开发中...', 'info');
    }
    
    /**
     * 删除记录（待实现）
     */
    deleteRecord(recordId) {
        if (!confirm('确定要删除这条记录吗？')) return;
        showToast('删除功能开发中...', 'info');
    }
    
    /**
     * 显示同步日志对话框（待实现）
     */
    showSyncLogsDialog() {
        showToast('同步历史功能开发中...', 'info');
    }

    /**
     * 绑定事件
     */
    /**
     * 切换批量清理下拉菜单
     */
    toggleBatchClearMenu(event) {
        event.stopPropagation();
        const menu = document.getElementById('batchClearMenu');
        if (menu) {
            const isVisible = menu.style.display !== 'none';
            menu.style.display = isVisible ? 'none' : 'block';
            
            // 点击其他地方关闭菜单
            if (!isVisible) {
                setTimeout(() => {
                    document.addEventListener('click', function closeMenu() {
                        menu.style.display = 'none';
                        document.removeEventListener('click', closeMenu);
                    });
                }, 0);
            }
        }
    }

    /**
     * 显示按时间清空对话框
     */
    showBatchClearByTimeDialog() {
        // 隐藏下拉菜单
        const menu = document.getElementById('batchClearMenu');
        if (menu) menu.style.display = 'none';

        const modalHtml = `
            <div id="batchClearByTimeModal" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(10px); display: flex; align-items: center; justify-content: center; z-index: 10000;">
                <div style="background: white; border-radius: 20px; width: 500px; max-width: 90%; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); overflow: hidden;">
                    <!-- 标题 -->
                    <div style="padding: 24px 24px 20px; border-bottom: 1px solid #f0f0f0;">
                        <h3 style="margin: 0; font-size: 20px; font-weight: 600; color: #1d1d1f; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-clock" style="color: #0071e3;"></i>
                            按时间清空数据
                        </h3>
                    </div>
                    
                    <!-- 内容 -->
                    <div style="padding: 24px;">
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #1d1d1f;">
                                选择时间范围
                            </label>
                            <select id="timeRange" style="width: 100%; padding: 12px; border: 1px solid #d1d1d6; border-radius: 10px; font-size: 14px; outline: none; transition: all 0.2s;">
                                <option value="7">7天前</option>
                                <option value="30">30天前</option>
                                <option value="90">90天前</option>
                                <option value="180">180天前</option>
                                <option value="365">365天前</option>
                            </select>
                        </div>
                        
                        <div style="background: #fff4e5; border-left: 4px solid #ff9500; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                            <div style="display: flex; gap: 12px;">
                                <i class="fas fa-exclamation-circle" style="color: #ff9500; margin-top: 2px;"></i>
                                <div style="flex: 1;">
                                    <div style="font-size: 14px; font-weight: 600; color: #1d1d1f; margin-bottom: 6px;">
                                        注意
                                    </div>
                                    <div style="font-size: 13px; color: #6e6e73; line-height: 1.5;">
                                        此操作将删除所选时间范围之前的所有数据记录，删除后无法恢复。
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 底部按钮 -->
                    <div style="padding: 16px 24px; background: #f5f5f7; display: flex; gap: 12px; justify-content: flex-end;">
                        <button onclick="closeModal('batchClearByTimeModal')" style="padding: 10px 24px; background: #e8e8ed; border: none; border-radius: 10px; font-size: 14px; font-weight: 500; color: #1d1d1f; cursor: pointer; transition: all 0.2s;">
                            取消
                        </button>
                        <button onclick="dataSourceManager.executeBatchClearByTime()" style="padding: 10px 24px; background: linear-gradient(180deg, #ff9500 0%, #ff6b00 100%); border: none; border-radius: 10px; font-size: 14px; font-weight: 600; color: white; cursor: pointer; box-shadow: 0 4px 12px rgba(255, 149, 0, 0.3); transition: all 0.2s;">
                            确认清空
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    /**
     * 执行按时间清空
     */
    async executeBatchClearByTime() {
        const days = document.getElementById('timeRange').value;
        
        try {
            const response = await fetch(`/api/data-source/${this.currentSourceId}/batch-clear`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    clear_type: 'by_time',
                    days: parseInt(days)
                })
            });

            const result = await response.json();

            if (result.code === 0) {
                showToast(`成功清空 ${days} 天前的数据`, 'success');
                closeModal('batchClearByTimeModal');
                await this.loadRecords();
                await this.viewDataSource(this.currentSourceId);
            } else {
                showToast(result.message || '清空失败', 'error');
            }
        } catch (error) {
            console.error('[批量清空] 出错:', error);
            showToast('清空失败，请重试', 'error');
        }
    }

    /**
     * 显示全部清空对话框
     */
    showBatchClearAllDialog() {
        // 隐藏下拉菜单
        const menu = document.getElementById('batchClearMenu');
        if (menu) menu.style.display = 'none';

        const sourceName = this.currentSource ? this.currentSource.name : '此数据源';

        const modalHtml = `
            <div id="batchClearAllModal" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(10px); display: flex; align-items: center; justify-content: center; z-index: 10000;">
                <div style="background: white; border-radius: 20px; width: 500px; max-width: 90%; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); overflow: hidden;">
                    <!-- 标题 -->
                    <div style="padding: 24px 24px 20px; border-bottom: 1px solid #f0f0f0;">
                        <h3 style="margin: 0; font-size: 20px; font-weight: 600; color: #d32f2f; display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-exclamation-triangle"></i>
                            全部清空数据
                        </h3>
                    </div>
                    
                    <!-- 内容 -->
                    <div style="padding: 24px;">
                        <div style="background: #ffebee; border-left: 4px solid #d32f2f; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                            <div style="display: flex; gap: 12px;">
                                <i class="fas fa-exclamation-triangle" style="color: #d32f2f; margin-top: 2px; font-size: 20px;"></i>
                                <div style="flex: 1;">
                                    <div style="font-size: 14px; font-weight: 600; color: #1d1d1f; margin-bottom: 8px;">
                                        ⚠️ 危险操作警告
                                    </div>
                                    <div style="font-size: 13px; color: #6e6e73; line-height: 1.6;">
                                        <p style="margin: 0 0 8px 0;">此操作将：</p>
                                        <ul style="margin: 0; padding-left: 20px;">
                                            <li>删除 <strong>${sourceName}</strong> 的所有数据记录</li>
                                            <li>清空所有字段定义</li>
                                            <li>重置表结构</li>
                                            <li>数据无法恢复</li>
                                        </ul>
                                        <p style="margin: 12px 0 0 0; color: #d32f2f; font-weight: 600;">
                                            后续导入或更新时将重新构建表结构
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #1d1d1f;">
                                输入数据源名称以确认：<span style="color: #d32f2f;">${sourceName}</span>
                            </label>
                            <input type="text" id="confirmSourceName" placeholder="请输入数据源名称" style="width: 100%; padding: 12px; border: 2px solid #d1d1d6; border-radius: 10px; font-size: 14px; outline: none; transition: all 0.2s; box-sizing: border-box;">
                        </div>
                    </div>
                    
                    <!-- 底部按钮 -->
                    <div style="padding: 16px 24px; background: #f5f5f7; display: flex; gap: 12px; justify-content: flex-end;">
                        <button onclick="closeModal('batchClearAllModal')" style="padding: 10px 24px; background: #e8e8ed; border: none; border-radius: 10px; font-size: 14px; font-weight: 500; color: #1d1d1f; cursor: pointer; transition: all 0.2s;">
                            取消
                        </button>
                        <button onclick="dataSourceManager.executeBatchClearAll()" style="padding: 10px 24px; background: linear-gradient(180deg, #d32f2f 0%, #c62828 100%); border: none; border-radius: 10px; font-size: 14px; font-weight: 600; color: white; cursor: pointer; box-shadow: 0 4px 12px rgba(211, 47, 47, 0.3); transition: all 0.2s;">
                            确认全部清空
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // 聚焦到输入框
        setTimeout(() => {
            document.getElementById('confirmSourceName').focus();
        }, 100);
    }

    /**
     * 执行全部清空
     */
    async executeBatchClearAll() {
        const inputName = document.getElementById('confirmSourceName').value.trim();
        const sourceName = this.currentSource ? this.currentSource.name : '';

        if (inputName !== sourceName) {
            showToast('数据源名称不匹配，请重新输入', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/data-source/${this.currentSourceId}/batch-clear`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    clear_type: 'all'
                })
            });

            const result = await response.json();

            if (result.code === 0) {
                showToast('数据已全部清空，表结构已重置', 'success');
                closeModal('batchClearAllModal');
                // 返回列表页
                this.backToList();
            } else {
                showToast(result.message || '清空失败', 'error');
            }
        } catch (error) {
            console.error('[全部清空] 出错:', error);
            showToast('清空失败，请重试', 'error');
        }
    }

    bindEvents() {
        // 新建数据源按钮
        const createBtn = document.getElementById('btnCreateDataSource');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.showCreateDialog());
        }
    }
}

// 创建全局实例
const dataSourceManager = new DataSourceManager();

// 暴露到全局
window.dataSourceManager = dataSourceManager;

// 标记已加载
window.dataSourceManagerReady = true;
console.log('[data-source.js] dataSourceManager 已准备就绪');

// 工具函数
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.remove();
    }
}

function copyText(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('success', '已复制到剪贴板');
    }).catch(err => {
        console.error('复制失败:', err);
        showToast('error', '复制失败');
    });
}
