/**
 * 客户列表页面增强功能
 * 版本：1.0
 * 日期：2026-01-27
 * 功能：头像悬停预览、筛选器增强等
 */

(function() {
    'use strict';
    
    // ==================== 头像悬停预览 ====================
    
    let avatarPreview = null;
    let previewTimeout = null;
    
    /**
     * 创建头像预览元素
     */
    function createAvatarPreview() {
        if (avatarPreview) return avatarPreview;
        
        avatarPreview = document.createElement('div');
        avatarPreview.className = 'avatar-preview';
        avatarPreview.innerHTML = '<img class="avatar-preview-image" alt="头像预览">';
        document.body.appendChild(avatarPreview);
        
        return avatarPreview;
    }
    
    /**
     * 显示头像预览
     */
    function showAvatarPreview(img, event) {
        clearTimeout(previewTimeout);
        
        previewTimeout = setTimeout(() => {
            const preview = createAvatarPreview();
            const previewImg = preview.querySelector('.avatar-preview-image');
            
            // 设置预览图片
            previewImg.src = img.src;
            previewImg.onerror = function() {
                hideAvatarPreview();
            };
            
            // 计算位置
            const rect = img.getBoundingClientRect();
            const previewSize = 200;
            const padding = 16;
            
            let left = rect.right + padding;
            let top = rect.top + (rect.height / 2) - (previewSize / 2);
            
            // 检查右侧空间
            if (left + previewSize > window.innerWidth) {
                left = rect.left - previewSize - padding;
            }
            
            // 检查顶部和底部空间
            if (top < padding) {
                top = padding;
            } else if (top + previewSize > window.innerHeight - padding) {
                top = window.innerHeight - previewSize - padding;
            }
            
            // 设置位置并显示
            preview.style.left = left + 'px';
            preview.style.top = top + 'px';
            preview.classList.add('show');
        }, 300); // 300ms延迟，避免快速滑过时频繁显示
    }
    
    /**
     * 隐藏头像预览
     */
    function hideAvatarPreview() {
        clearTimeout(previewTimeout);
        if (avatarPreview) {
            avatarPreview.classList.remove('show');
        }
    }
    
    /**
     * 初始化头像预览功能
     */
    function initAvatarPreview() {
        // 使用事件委托监听所有头像
        document.addEventListener('mouseover', function(e) {
            const avatar = e.target.closest('.customer-avatar');
            if (avatar && avatar.src) {
                showAvatarPreview(avatar, e);
            }
        });
        
        document.addEventListener('mouseout', function(e) {
            const avatar = e.target.closest('.customer-avatar');
            if (avatar) {
                hideAvatarPreview();
            }
        });
        
        console.log('[客户列表增强] 头像预览功能已初始化');
    }
    
    // ==================== 筛选器增强 ====================
    
    /**
     * 增强筛选器交互
     */
    function enhanceFilters() {
        const filterInputs = document.querySelectorAll('.filter-input');
        const filterSelects = document.querySelectorAll('.filter-select');
        const filterTagSelects = document.querySelectorAll('.filter-tag-select');
        
        // 为所有筛选输入添加清除功能
        filterInputs.forEach(input => {
            if (input.type === 'text') {
                input.addEventListener('input', function() {
                    if (this.value) {
                        this.style.paddingRight = '32px';
                    } else {
                        this.style.paddingRight = '12px';
                    }
                });
            }
        });
        
        // 增强下拉选择器
        filterSelects.forEach(select => {
            select.addEventListener('change', function() {
                if (this.value) {
                    this.style.fontWeight = '500';
                    this.style.color = 'var(--text-primary)';
                } else {
                    this.style.fontWeight = '400';
                    this.style.color = 'var(--text-secondary)';
                }
            });
        });
        
        console.log('[客户列表增强] 筛选器增强已初始化');
    }
    
    // ==================== 表格增强 ====================
    
    /**
     * 增强表格交互
     */
    function enhanceTable() {
        const table = document.getElementById('customers-table');
        if (!table) return;
        
        // 添加表格行点击高亮效果
        const tbody = table.querySelector('tbody');
        if (tbody) {
            tbody.addEventListener('click', function(e) {
                const row = e.target.closest('tr');
                if (row && !e.target.closest('input[type="checkbox"]')) {
                    // 移除其他行的高亮
                    tbody.querySelectorAll('tr').forEach(r => {
                        r.style.background = '';
                    });
                    
                    // 高亮当前行
                    row.style.background = 'rgba(0, 122, 255, 0.08)';
                    
                    // 3秒后移除高亮
                    setTimeout(() => {
                        row.style.background = '';
                    }, 3000);
                }
            });
        }
        
        console.log('[客户列表增强] 表格增强已初始化');
    }
    
    // ==================== 初始化 ====================
    
    /**
     * 页面加载完成后初始化所有增强功能
     */
    function init() {
        // 延迟初始化，确保DOM完全加载
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(initAll, 100);
            });
        } else {
            setTimeout(initAll, 100);
        }
    }
    
    function initAll() {
        initAvatarPreview();
        enhanceFilters();
        enhanceTable();
        console.log('[客户列表增强] 所有增强功能已加载');
    }
    
    // 立即执行初始化
    init();
    
    // 暴露到全局，供其他脚本调用
    window.CustomerListEnhancer = {
        refreshAvatarPreview: initAvatarPreview,
        refreshFilters: enhanceFilters,
        refreshTable: enhanceTable
    };
    
})();
