// ========== 客户画像模块 ==========

// 加载客户画像数据
async function loadCustomerPortrait() {
    try {
        // 加载标签统计
        loadTagStats();
        // 加载省份统计
        loadProvinceStats();
        // 加载添加方式统计
        loadAddWayStats();
        // 加载性别统计
        loadGenderStats();
    } catch (error) {
        console.error('加载客户画像失败:', error);
    }
}

// 加载标签统计
async function loadTagStats() {
    try {
        const response = await fetch(`/api/customer-portrait/tag-stats?api_token=${apiToken}`);
        const result = await response.json();
        
        if (result.success) {
            const keyTags = result.data.key_tags;
            
            // 更新卡片数据
            document.querySelector('#stat-user .stat-value').textContent = keyTags['用户标签'] + '人';
            document.querySelector('#stat-agent .stat-value').textContent = keyTags['代理商'] + '人';
            document.querySelector('#stat-partner .stat-value').textContent = keyTags['合伙人'] + '人';
            document.querySelector('#stat-supplier .stat-value').textContent = keyTags['供应商'] + '人';
            document.querySelector('#stat-peer .stat-value').textContent = keyTags['同行'] + '人';
            document.querySelector('#stat-old-agent .stat-value').textContent = keyTags['原有老代理'] + '人';
        }
    } catch (error) {
        console.error('加载标签统计失败:', error);
    }
}

// 加载省份统计
async function loadProvinceStats() {
    try {
        const response = await fetch(`/api/customer-portrait/province-stats?api_token=${apiToken}`);
        const result = await response.json();
        
        if (result.success) {
            const provinceList = document.getElementById('province-list');
            const provinces = result.data;
            
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
        }
    } catch (error) {
        console.error('加载省份统计失败:', error);
    }
}

// 加载添加方式统计（饼图）
async function loadAddWayStats() {
    try {
        const response = await fetch(`/api/customer-portrait/add-way-stats?api_token=${apiToken}`);
        const result = await response.json();
        
        if (result.success) {
            const items = result.data.items;
            
            // 使用简单的饼图显示
            renderPieChart('add-way-chart', items, 'way', 'count');
        }
    } catch (error) {
        console.error('加载添加方式统计失败:', error);
    }
}

// 加载性别统计（饼图）
async function loadGenderStats() {
    try {
        const response = await fetch(`/api/customer-portrait/gender-stats?api_token=${apiToken}`);
        const result = await response.json();
        
        if (result.success) {
            const items = result.data.items;
            
            // 使用简单的饼图显示
            renderPieChart('gender-chart', items, 'gender', 'count');
        }
    } catch (error) {
        console.error('加载性别统计失败:', error);
    }
}

// 渲染简单饼图
function renderPieChart(containerId, data, labelKey, valueKey) {
    const container = document.getElementById(containerId);
    
    if (!data || data.length === 0) {
        container.innerHTML = '<div style="color: #999; padding: 50px; text-align: center;">暂无数据</div>';
        return;
    }
    
    const total = data.reduce((sum, item) => sum + item[valueKey], 0);
    
    const colors = ['#667eea', '#f5576c', '#43e97b', '#fccb90', '#4facfe', '#fa709a'];
    
    let html = '<div style="display: flex; align-items: center; justify-content: space-around; height: 100%;">';
    
    // 饼图（简化版，用圆环图表示）
    html += '<div style="position: relative; width: 150px; height: 150px;">';
    
    let currentAngle = 0;
    data.forEach((item, index) => {
        const percentage = (item[valueKey] / total) * 100;
        const angle = (item[valueKey] / total) * 360;
        
        const color = colors[index % colors.length];
        
        html += `
            <div style="
                position: absolute;
                width: 100%;
                height: 100%;
                border-radius: 50%;
                background: conic-gradient(
                    ${color} 0deg ${angle}deg,
                    transparent ${angle}deg 360deg
                );
                transform: rotate(${currentAngle}deg);
            "></div>
        `;
        
        currentAngle += angle;
    });
    
    html += '<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 80px; height: 80px; background: white; border-radius: 50%;"></div>';
    html += '</div>';
    
    // 图例
    html += '<div style="display: flex; flex-direction: column; gap: 8px;">';
    data.forEach((item, index) => {
        const color = colors[index % colors.length];
        const percentage = ((item[valueKey] / total) * 100).toFixed(1);
        
        html += `
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 12px; height: 12px; border-radius: 2px; background: ${color};"></div>
                <div style="font-size: 14px; color: #666;">
                    ${item[labelKey]}: <strong style="color: #333;">${item[valueKey]}人</strong> (${percentage}%)
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
    setTimeout(() => {
        showToast('数据刷新完成', 'success');
    }, 500);
}

// 刷新客户画像时也加载数据
window.loadCustomerPortraitData = loadCustomerPortrait;

// 当切换到客户画像模块时加载数据
document.addEventListener('DOMContentLoaded', () => {
    // 监听模块切换
    const customerProfileNav = document.querySelector('[data-module="customer-profile"]');
    if (customerProfileNav) {
        customerProfileNav.addEventListener('click', () => {
            // 延迟加载，确保DOM已渲染
            setTimeout(() => {
                loadCustomerPortrait();
            }, 100);
        });
    }
});

// 如果页面已经在客户画像模块，立即加载
setTimeout(() => {
    const module = document.getElementById('module-customer-profile');
    if (module && module.classList.contains('active')) {
        loadCustomerPortrait();
    }
}, 200);
