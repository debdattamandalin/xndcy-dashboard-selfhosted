// Global Custom Modal Implementation
window.showModal = function({ title, message, type = 'info', isConfirm = false }) {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 bg-black/60 backdrop-blur-sm z-[200] flex items-center justify-center p-4 opacity-0 transition-opacity duration-200';
        
        let icon = 'info';
        let iconColor = 'text-primary';
        let iconBg = 'bg-primary/10';
        
        if (type === 'error' || type === 'danger') {
            icon = 'warning';
            iconColor = 'text-error';
            iconBg = 'bg-error/10';
        } else if (type === 'success') {
            icon = 'check_circle';
            iconColor = 'text-[#00e676]';
            iconBg = 'bg-[#00e676]/10';
        }

        overlay.innerHTML = `
            <div class="bg-surface-container border border-outline-variant/30 rounded-3xl shadow-2xl max-w-md w-full transform scale-95 transition-transform duration-200 overflow-hidden">
                <div class="p-8">
                    <div class="flex gap-5 items-start">
                        <div class="w-12 h-12 shrink-0 rounded-full ${iconBg} flex items-center justify-center border border-outline-variant/10">
                            <span class="material-symbols-outlined ${iconColor} text-[24px]">${icon}</span>
                        </div>
                        <div class="flex-1 pt-1 text-left">
                            <h3 class="font-headline-sm text-[18px] font-semibold text-on-surface tracking-tight mb-2">${title}</h3>
                            <p class="text-[14px] text-on-surface-variant/80 leading-relaxed">${message}</p>
                        </div>
                    </div>
                </div>
                <div class="px-8 py-5 bg-surface-container-high/30 border-t border-outline-variant/10 flex justify-end gap-3">
                    ${isConfirm ? `<button class="modal-cancel-btn px-6 py-2.5 rounded-xl font-medium text-[13px] text-on-surface-variant hover:text-on-surface hover:bg-surface-container-highest transition-colors">Cancel</button>` : ''}
                    <button class="modal-confirm-btn px-6 py-2.5 rounded-xl font-medium text-[13px] transition-all flex items-center gap-2 shadow-lg hover:-translate-y-0.5 ${type === 'danger' ? 'bg-error text-on-error shadow-error/20 hover:shadow-error/40 hover:bg-error/90' : 'bg-primary text-on-primary shadow-primary/20 hover:shadow-primary/40 hover:bg-primary/90'}">${isConfirm ? (type === 'danger' ? 'Delete' : 'Confirm') : 'Okay'}</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Trigger animation
        requestAnimationFrame(() => {
            overlay.classList.remove('opacity-0');
            overlay.querySelector('div').classList.remove('scale-95');
        });
        
        const close = (result) => {
            overlay.classList.add('opacity-0');
            overlay.querySelector('div').classList.add('scale-95');
            setTimeout(() => {
                overlay.remove();
                resolve(result);
            }, 200);
        };
        
        const confirmBtn = overlay.querySelector('.modal-confirm-btn');
        confirmBtn.addEventListener('click', () => close(true));
        confirmBtn.focus();
        
        if (isConfirm) {
            overlay.querySelector('.modal-cancel-btn').addEventListener('click', () => close(false));
        }
    });
};

window.showAlert = function(title, message, type = 'info') {
    return window.showModal({ title, message, type, isConfirm: false });
};

window.showConfirm = function(title, message, type = 'danger') {
    return window.showModal({ title, message, type, isConfirm: true });
};

// Global Custom Select Implementation
window.initCustomSelects = function() {
    document.querySelectorAll('select:not([data-custom-select-initialized])').forEach(select => {
        select.setAttribute('data-custom-select-initialized', 'true');
        select.style.display = 'none'; // Hide native select
        
        // Wrap select if not already in a wrapper we control
        const wrapper = document.createElement('div');
        wrapper.className = 'relative w-full';
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(select);
        
        // Remove native dropdown chevron if it exists as a sibling
        const sibling = wrapper.nextElementSibling;
        if (sibling && sibling.querySelector && sibling.querySelector('span.material-symbols-outlined') && sibling.textContent.includes('expand_more')) {
            sibling.remove(); // Remove hardcoded chevron in users_add.html
        }

        // Create Custom Button
        const button = document.createElement('div');
        // Copy some classes from original select for consistent height/border, but use flex layout
        button.className = 'w-full bg-surface-container-high border border-outline-variant/20 rounded-xl px-4 py-3 h-[46px] flex items-center justify-between cursor-pointer font-body-md text-[14px] text-on-surface hover:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50 transition-all';
        button.tabIndex = 0;
        
        const displaySpan = document.createElement('span');
        displaySpan.className = 'truncate pointer-events-none';
        
        const selectedOption = select.options[select.selectedIndex];
        displaySpan.textContent = selectedOption ? selectedOption.textContent : 'Select...';
        
        const iconSpan = document.createElement('span');
        iconSpan.className = 'material-symbols-outlined text-on-surface-variant text-[18px] transition-transform duration-300 pointer-events-none';
        iconSpan.textContent = 'expand_more';
        
        button.appendChild(displaySpan);
        button.appendChild(iconSpan);
        
        // Create Dropdown Menu
        const dropdown = document.createElement('div');
        dropdown.className = 'absolute left-0 right-0 top-full mt-2 bg-surface-container border border-outline-variant/30 rounded-xl shadow-2xl overflow-hidden z-[150] opacity-0 pointer-events-none transform -translate-y-2 transition-all duration-200 backdrop-blur-md';
        
        const list = document.createElement('ul');
        list.className = 'max-h-[250px] overflow-y-auto py-2 custom-scrollbar';
        dropdown.appendChild(list);
        
        // Populate options
        Array.from(select.options).forEach(option => {
            if (option.disabled && !option.value) return; // Skip placeholder usually
            
            const li = document.createElement('li');
            li.className = 'px-4 py-2.5 text-[13px] text-on-surface hover:bg-white/5 cursor-pointer flex items-center transition-colors';
            if (select.value === option.value) {
                li.classList.add('bg-primary/10', 'text-primary');
            }
            
            // Selected checkmark
            const check = document.createElement('span');
            check.className = 'material-symbols-outlined text-[16px] mr-2 transition-opacity';
            check.textContent = 'check';
            check.style.opacity = select.value === option.value ? '1' : '0';
            
            const text = document.createElement('span');
            text.textContent = option.textContent;
            
            li.appendChild(check);
            li.appendChild(text);
            
            li.addEventListener('click', (e) => {
                e.stopPropagation();
                select.value = option.value;
                displaySpan.textContent = option.textContent;
                
                // Update checkmarks
                Array.from(list.children).forEach(child => {
                    child.classList.remove('bg-primary/10', 'text-primary');
                    child.querySelector('span').style.opacity = '0';
                });
                li.classList.add('bg-primary/10', 'text-primary');
                check.style.opacity = '1';
                
                // Close dropdown
                closeDropdown();
                
                // Trigger change event for original select
                select.dispatchEvent(new Event('change', { bubbles: true }));
            });
            
            list.appendChild(li);
        });
        
        wrapper.appendChild(button);
        wrapper.appendChild(dropdown);
        
        // Toggle logic
        let isOpen = false;
        
        const openDropdown = () => {
            // Close others
            document.querySelectorAll('.custom-select-dropdown-open').forEach(d => {
                if (d !== dropdown) {
                    d.classList.remove('opacity-100', 'pointer-events-auto', 'translate-y-0', 'custom-select-dropdown-open');
                    d.classList.add('opacity-0', 'pointer-events-none', '-translate-y-2');
                    const icon = d.previousElementSibling?.querySelector('.material-symbols-outlined:last-child');
                    if (icon) icon.style.transform = 'rotate(0deg)';
                }
            });
            
            dropdown.classList.remove('opacity-0', 'pointer-events-none', '-translate-y-2');
            dropdown.classList.add('opacity-100', 'pointer-events-auto', 'translate-y-0', 'custom-select-dropdown-open');
            iconSpan.style.transform = 'rotate(180deg)';
            button.classList.add('border-primary/50');
            
            // Elevate parent stacking context
            const parentItem = wrapper.closest('.gsap-stagger-item') || wrapper.parentElement;
            if(parentItem) {
                parentItem.dataset.origZIndex = parentItem.style.zIndex || '';
                parentItem.style.zIndex = '100';
                parentItem.style.position = parentItem.style.position || 'relative';
            }
            
            isOpen = true;
        };
        
        const closeDropdown = () => {
            dropdown.classList.remove('opacity-100', 'pointer-events-auto', 'translate-y-0', 'custom-select-dropdown-open');
            dropdown.classList.add('opacity-0', 'pointer-events-none', '-translate-y-2');
            iconSpan.style.transform = 'rotate(0deg)';
            button.classList.remove('border-primary/50');
            
            // Restore parent stacking context
            const parentItem = wrapper.closest('.gsap-stagger-item') || wrapper.parentElement;
            if(parentItem && parentItem.dataset.origZIndex !== undefined) {
                parentItem.style.zIndex = parentItem.dataset.origZIndex;
            }
            
            isOpen = false;
        };
        
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            if (isOpen) closeDropdown();
            else openDropdown();
        });
        
        // Close on click outside
        document.addEventListener('click', (e) => {
            if (isOpen && !wrapper.contains(e.target)) {
                closeDropdown();
            }
        });
    });
};

// Initialize on page load and HTMX swaps
document.addEventListener('DOMContentLoaded', window.initCustomSelects);
document.body.addEventListener('htmx:afterSwap', window.initCustomSelects);
