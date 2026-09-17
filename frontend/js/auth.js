/**
 * CHROMA BLEND — Authentication Controller
 */

async function checkAuthState() {
  try {
    const res = await API.get('/auth/me');
    if (res && res.data) {
      // Update greeting in header if elements exist
      const userSpan = document.getElementById('current-user-name');
      if (userSpan) {
        userSpan.textContent = res.data.name;
      }
      return res.data;
    }
  } catch (err) {
    // If not authenticated and on a protected page, redirect
    const isProtected = window.location.pathname.includes('planner') || window.location.pathname.includes('private');
    if (isProtected) {
      window.location.href = '/login.html';
    }
  }
  return null;
}

async function handleLogout() {
  try {
    await API.post('/auth/logout');
    window.location.href = '/login.html';
  } catch (err) {
    showToast('Failed to logout. Please try again.', 'error');
  }
}

// Attach forms if present on page
document.addEventListener('DOMContentLoaded', () => {
  // Login Form
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorBanner = document.getElementById('auth-error');
      const submitBtn = loginForm.querySelector('button[type="submit"]');
      
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;

      errorBanner.style.display = 'none';
      submitBtn.disabled = true;
      submitBtn.textContent = 'Verifying...';

      try {
        const res = await API.post('/auth/login', { email, password });
        if (res && res.success) {
          window.location.href = '/planner.html';
        }
      } catch (err) {
        errorBanner.textContent = err.message || 'Login failed. Please check credentials.';
        errorBanner.style.display = 'block';
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign In';
      }
    });
  }

  // Registration Form
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorBanner = document.getElementById('auth-error');
      const submitBtn = registerForm.querySelector('button[type="submit"]');
      
      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const passcode = (document.getElementById('passcode').value || '1984').trim();

      errorBanner.style.display = 'none';
      submitBtn.disabled = true;
      submitBtn.textContent = 'Creating account...';

      try {
        const res = await API.post('/auth/register', { name, email, password, passcode });
        if (res && res.success) {
          showToast('Account created successfully!', 'success');
          setTimeout(() => {
            window.location.href = '/planner.html';
          }, 400);
        }
      } catch (err) {
        errorBanner.textContent = err.message || 'Registration failed.';
        errorBanner.style.display = 'block';
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
      }
    });
  }

  // Bind logout buttons
  document.querySelectorAll('.logout-trigger').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      handleLogout();
    });
  });
});
