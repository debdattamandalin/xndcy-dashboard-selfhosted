document.addEventListener('DOMContentLoaded', async () => {
    // Check if already logged in
    try {
        const sessionRes = await fetch('/api/check_session');
        const sessionData = await sessionRes.json();
        if (sessionData.logged_in && (window.location.pathname === '/' || window.location.pathname === '/login')) {
            window.location.href = '/dashboard';
            return;
        }
    } catch(e) {
        // ignore
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const emailInput = document.getElementById('email').value;
            const passwordInput = document.getElementById('password').value;
            const rememberInput = document.getElementById('remember').checked;
            const errorMsg = document.getElementById('error-message');
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        email: emailInput, 
                        password: passwordInput,
                        remember: rememberInput
                    })
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    errorMsg.classList.add('hidden');
                    window.location.href = '/dashboard';
                } else {
                    errorMsg.textContent = data.message || 'Invalid email or password.';
                    errorMsg.classList.remove('hidden');
                }
            } catch (error) {
                errorMsg.textContent = 'Server error. Please try again later.';
                errorMsg.classList.remove('hidden');
            }
        });
    }

    const ssoBtn = document.getElementById('sso-btn');
    if (ssoBtn) {
        ssoBtn.addEventListener('click', function() {
            window.location.href = '/dashboard';
        });
    }

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await fetch('/api/logout', { method: 'POST' });
                window.location.href = '/login';
            } catch (err) {
                console.error("Logout failed", err);
            }
        });
    }
});
