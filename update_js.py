import re

def update_file(filename, btn_class):
    with open(filename, 'r') as f:
        content = f.read()

    # Find the script block
    script_start = content.find('(() => {')
    script_end = content.find('})();', script_start) + 5
    
    if script_start == -1 or script_end == -1:
        print(f"Script block not found in {filename}")
        return

    new_script = f"""(() => {{
    // Search functionality
    const searchInput = document.getElementById('{filename.replace("templates/", "").replace(".html", "")}-search');
    const tableBody = document.querySelector('tbody');
    const rows = tableBody ? tableBody.querySelectorAll('tr.group') : [];
    
    if (searchInput) {{
        searchInput.addEventListener('input', (e) => {{
            const term = e.target.value.toLowerCase();
            let hasVisible = false;
            
            rows.forEach(row => {{
                const nameEl = row.querySelector('.{filename.replace("templates/", "").replace(".html", "")}-name-text') || row.querySelector('td');
                if (nameEl) {{
                    const name = nameEl.textContent.toLowerCase();
                    if (name.includes(term)) {{
                        row.style.display = '';
                        hasVisible = true;
                    }} else {{
                        row.style.display = 'none';
                    }}
                }}
            }});
            
            let emptyRow = document.getElementById('empty-search-row');
            if (!hasVisible && rows.length > 0) {{
                if (!emptyRow) {{
                    emptyRow = document.createElement('tr');
                    emptyRow.id = 'empty-search-row';
                    emptyRow.innerHTML = '<td colspan="5" class="px-8 py-12 text-center text-on-surface-variant/60 font-medium">No results match your search.</td>';
                    tableBody.appendChild(emptyRow);
                }}
                emptyRow.style.display = '';
            }} else if (emptyRow) {{
                emptyRow.style.display = 'none';
            }}
        }});
    }}

    // Relocate dropdowns to body
    const actionBtns = document.querySelectorAll('{".action-menu-btn" if "roles" in filename else ".action-btn"}');
    
    actionBtns.forEach((btn, idx) => {{
        const dropdown = btn.nextElementSibling || document.getElementById(btn.dataset.targetId);
        if (dropdown && dropdown.classList.contains('action-dropdown')) {{
            dropdown.id = `action-dropdown-${{idx}}-{filename.replace("templates/", "").replace(".html", "")}`;
            btn.dataset.targetId = dropdown.id;
            document.body.appendChild(dropdown);
        }}
    }});

    // Global event delegation for dropdowns and actions to survive HTMX swaps
    if (window._dropdownHandler) {{
        document.body.removeEventListener('click', window._dropdownHandler);
        window.removeEventListener('scroll', window._scrollHandler, true);
    }}

    window._closeAllDropdowns = () => {{
        document.querySelectorAll('.action-dropdown').forEach(d => d.classList.add('hidden'));
    }};

    window._scrollHandler = () => window._closeAllDropdowns();
    window.addEventListener('scroll', window._scrollHandler, true);

    window._dropdownHandler = async (e) => {{
        // Handle dropdown toggle
        const toggleBtn = e.target.closest('.action-menu-btn, .action-btn');
        if (toggleBtn) {{
            e.stopPropagation();
            const targetId = toggleBtn.dataset.targetId;
            if (!targetId) return;
            
            const dropdown = document.getElementById(targetId);
            if (!dropdown) return;
            
            const isHidden = dropdown.classList.contains('hidden');
            window._closeAllDropdowns();
            
            if (isHidden) {{
                const rect = toggleBtn.getBoundingClientRect();
                dropdown.style.top = `${{rect.bottom + window.scrollY + 8}}px`;
                dropdown.style.left = `${{rect.right + window.scrollX - 192}}px`;
                dropdown.classList.remove('hidden');
            }}
            return;
        }}

        // Prevent closing if clicking inside dropdown
        if (e.target.closest('.action-dropdown')) {{
            // Handle delete action
            const deleteBtn = e.target.closest('{btn_class}');
            if (deleteBtn) {{
                e.preventDefault();
                e.stopPropagation();
                
                const id = deleteBtn.dataset.roleId || deleteBtn.dataset.userId;
                if (!id) return;
                
                const entityType = deleteBtn.classList.contains('delete-role-btn') ? 'role' : 'user';
                const endpoint = deleteBtn.classList.contains('delete-role-btn') ? `/api/roles/${{id}}` : `/api/users/${{id}}`;
                
                if (typeof window.showConfirm !== 'function') {{
                    alert('Error: UI modals not loaded correctly. Please hard refresh.');
                    return;
                }}

                const confirmed = await window.showConfirm(`Delete ${{entityType === 'role' ? 'Role' : 'User'}}`, `Are you sure you want to delete this ${{entityType}}? This cannot be undone.`, 'danger');
                if (!confirmed) return;
                
                window._closeAllDropdowns();
                
                try {{
                    const response = await fetch(endpoint, {{ method: 'DELETE' }});
                    const data = await response.json();
                    
                    if (data.success) {{
                        window.location.reload();
                    }} else {{
                        await window.showAlert('Error', data.message, 'error');
                    }}
                }} catch (err) {{
                    await window.showAlert('Network Error', 'A network error occurred. Please try again.', 'error');
                }}
            }}
            return;
        }}

        // Close dropdowns when clicking outside
        window._closeAllDropdowns();
    }};

    document.body.addEventListener('click', window._dropdownHandler);
}})();"""

    # Only replace if the script is found
    new_content = content[:script_start] + new_script + content[script_end:]
    
    with open(filename, 'w') as f:
        f.write(new_content)
    print(f"Updated {filename}")

update_file('templates/roles.html', '.delete-role-btn')
update_file('templates/users.html', '.delete-user-btn')
