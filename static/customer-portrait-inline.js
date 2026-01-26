
// ========== 客户画像模块 ==========

// 加载客户画像数据
async function loadCustomerPortrait() {
    console.log('[客户画像] 开始加载数据...');
    try {
        // 加载标签统计
        await loadTagStats();
        // 加载省份统计
        await loadProvinceStats();
        // 加载添加方式统计
        await loadAddWayStats();
        // 加载性别统计
        await loadGenderStats();
        console.log('[客户画像] 所有数据加载完成');
    } catch (error) {
        console.error('[客户画像] 加载失败:', error);
        showToast('加载客户画像数据失败', 'error');
    }
}

// 加载标签统计
async function loadTagStats() {
    try {
        console.log('[标签统计] 开始加载...');
        const response = await fetch(`/api/customer-portrait/tag-stats?api_token=${apiToken}`);
        const result = await response.json();
        
        if (result.success) {
            const keyTags = result.data.key_tags;
            console.log('[标签统计] 数据:', keyTags);
            
            // 更新卡片数据
            const updateStat = (id, value) => {
                const elem = document.querySelector(`#${id} .stat-value`);
                if (elem) {
                    elem.textContent = value + '人';
                } else {
                    console.warn(`[标签统计] 元素 #${id} 不存在`);
                }
            };
            
            updateStat('stat-user', keyTags['用户标签']);
            updateStat('stat-agent', keyTags['代理商']);
            updateStat('stat-partner', keyTags['合伙人']);
            updateStat('stat-supplier', keyTags['供应商']);
            updateStat('stat-peer', keyTags['同行']);
            updateStat('stat-old-agent', keyTags['原有老代理']);
            
            console.log('[标签统计] 加载完成');
        } else {
            console.error('[标签统计] API返回失败:', result.message);
        }
    } catch (error) {
        console.error('[标签统计] 加载失败:', error);
    }
}

// 加载省份统计
async function loadProvinceStats() {
    try {
        console.log('[省份统计] 开始加载...');
        const response = await fetch(`/api/customer-portrait/province-stats?api_token=${apiToken}`);
        const result = await response.json();
        
        if (result.success) {
            const provinceList = document.getElementById('province-list');
            if (!provinceList) {
                console.warn('[省份统计] 元素 #province-list 不存在');
                return;
            }
            
            const provinces = result.data;
            console.log('[省份统计] 数据:', provinces);
            
            if (Object.keys(provinces).length === 0) {
                provinceList.innerHTML = '<div style="color: #999; padding: 20px;">暂无省份数据</div>';
                return;
            }
            
            // 渲染省份标签
            const colors = [
                'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                'linear-gradient(135deg, #fccb90 0%, #d57eeb 100%)',
                'linear-gradient(135deg, #FF6B1A 0%, #E65100 100%)'
            ];
            
            let html = '';
            let colorIndex = 0;
            
            for (const [province, count] of Object.entries(provinces)) {
                const color = colors[colorIndex % colors.length];
                html += `
                    <div class="province-tag" style="background: ${color};">
                        ${province}
                        <span class="count">${count}人</span>
                    </div>
                `;
                colorIndex++;
            }
            
            provinceList.innerHTML = html;
            console.log('[省份统计] 加载完成');
        } else {
            console.error('[省份统计] API返回失败:', result.message);
        }
    } catch (error) {
        console.error('[省份统计] 加载失败:', error);
    }
}

// 加载添加方式统计（饼图）
async function loadAddWayStats() {
    try {
        console.log('[添加方式统计] 开始加载...');
        const response = await fetch(`/api/customer-portrait/add-way-stats?api_token=${apiToken}`);
        const result = await response.json();
        
        if (result.success) {
            const items = result.data.items;
            console.log('[添加方式统计] 数据:', items);
            
            // 使用简单的饼图显示
            renderPieChart('add-way-chart', items, 'way', 'count');
            console.log('[添加方式统计] 加载完成');
        } else {
            console.error('[添加方式统计] API返回失败:', result.message);
        }
    } catch (error) {
        console.error('[添加方式统计] 加载失败:', error);
    }
}

// 加载性别统计（饼图）
async function loadGenderStats() {
    try {
        console.log('[性别统计] 开始加载...');
        const response = await fetch(`/api/customer-portrait/gender-stats?api_token=${apiToken}`);
        const result = await response.json();
        
        if (result.success) {
            const items = result.data.items;
            console.log('[性别统计] 数据:', items);
            
            // 使用简单的饼图显示
            renderPieChart('gender-chart', items, 'gender', 'count');
            console.log('[性别统计] 加载完成');
        } else {
            console.error('[性别统计] API返回失败:', result.message);
        }
    } catch (error) {
        console.error('[性别统计] 加载失败:', error);
    }
}

// 渲染简单饼图
function renderPieChart(containerId, data, labelKey, valueKey) {
    const container = document.getElementById(containerId);
    
    if (!container) {
        console.warn(`[饼图] 元素 #${containerId} 不存在`);
        return;
    }
    
    if (!data || data.length === 0) {
        container.innerHTML = '<div style="color: #999; padding: 50px; text-align: center;">暂无数据</div>';
        return;
    }
    
    const total = data.reduce((sum, item) => sum + item[valueKey], 0);
    
    const colors = ['#667eea', '#f5576c', '#43e97b', '#fccb90', '#4facfe', '#fa709a', '#764ba2', '#38f9d7'];
    
    let html = '<div style="display: flex; align-items: center; justify-content: space-around; height: 100%; padding: 20px;">';
    
    // 图例（列表形式）
    html += '<div style="display: flex; flex-direction: column; gap: 12px; width: 100%;">';
    data.forEach((item, index) => {
        const color = colors[index % colors.length];
        const percentage = ((item[valueKey] / total) * 100).toFixed(1);
        
        html += `
            <div style="display: flex; align-items: center; gap: 15px; padding: 10px; background: #f8f9fa; border-radius: 6px;">
                <div style="width: 16px; height: 16px; border-radius: 3px; background: ${color}; flex-shrink: 0;"></div>
                <div style="flex: 1; font-size: 14px; color: #666;">
                    ${item[labelKey]}
                </div>
                <div style="font-size: 16px; font-weight: 600; color: #333;">
                    ${item[valueKey]}人
                </div>
                <div style="font-size: 13px; color: #999;">
                    ${percentage}%
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    html += '</div>';
    
    container.innerHTML = html;
}

// 刷新客户画像
function refreshCustomerPortrait() {
    showToast('正在刷新数据...', 'info');
    loadCustomerPortrait();
}

// 在全局作用域暴露函数
window.loadCustomerPortrait = loadCustomerPortrait;
window.refreshCustomerPortrait = refreshCustomerPortrait;

console.log('[客户画像] 模块初始化完成');
