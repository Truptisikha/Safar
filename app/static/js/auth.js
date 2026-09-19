/* Client-side checks for sign-in and sign-up. The server validates again. */

function showError(input, message) {
  input.classList.add('invalid');
  const slot = input.parentElement.querySelector('.field-error');
  if (slot) { slot.textContent = message; slot.style.display = 'block'; }
}

function clearError(input) {
  input.classList.remove('invalid');
  const slot = input.parentElement.querySelector('.field-error');
  if (slot) slot.style.display = 'none';
}

const RULES = {
  name: (v) => (v.trim() ? '' : 'Enter your name.'),
  email: (v) => (/^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$/.test(v.trim()) ? '' : 'Enter a valid email address.'),
  phone: (v) => (!v || /^[0-9]{10}$/.test(v.trim()) ? '' : 'Phone number must be 10 digits.'),
  password: (v) => (v.length >= 6 ? '' : 'Password must be at least 6 characters.'),
};

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form[data-validate="auth"]');
  if (!form) return;

  form.querySelectorAll('input').forEach((input) => {
    input.addEventListener('input', () => clearError(input));
  });

  form.addEventListener('submit', (e) => {
    let firstBad = null;

    form.querySelectorAll('input[name]').forEach((input) => {
      const rule = RULES[input.name];
      if (!rule) return;
      const message = rule(input.value);
      if (message) {
        showError(input, message);
        firstBad = firstBad || input;
      }
    });

    const pass = form.querySelector('input[name="password"]');
    const confirm = form.querySelector('input[name="confirm_password"]');
    if (confirm && pass.value !== confirm.value) {
      showError(confirm, 'Passwords do not match.');
      firstBad = firstBad || confirm;
    }

    if (firstBad) {
      e.preventDefault();
      firstBad.focus();
    }
  });
});
