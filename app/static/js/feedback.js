/* Star rating input and the edit-in-place dialog for a review. */

document.addEventListener('DOMContentLoaded', () => {
  /* star pickers */
  document.querySelectorAll('[data-stars]').forEach((picker) => {
    const hidden = picker.parentElement.querySelector('input[name="rating"]');
    const buttons = [...picker.querySelectorAll('button')];

    const paint = (upto) => buttons.forEach((b, i) => {
      b.textContent = i < upto ? '★' : '☆';
    });

    buttons.forEach((btn, i) => {
      btn.type = 'button';
      btn.addEventListener('click', () => { hidden.value = i + 1; paint(i + 1); });
      btn.addEventListener('mouseenter', () => paint(i + 1));
    });
    picker.addEventListener('mouseleave', () => paint(Number(hidden.value || 0)));
    paint(Number(hidden.value || 0));
  });

  /* load the chosen review into the edit modal */
  document.querySelectorAll('[data-edit-feedback]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const form = document.querySelector('#editFeedbackForm');
      form.action = btn.dataset.action;
      form.querySelector('textarea[name="message"]').value = btn.dataset.message;
      const rating = form.querySelector('input[name="rating"]');
      rating.value = btn.dataset.rating;
      form.querySelectorAll('[data-stars] button').forEach((s, i) => {
        s.textContent = i < Number(btn.dataset.rating) ? '★' : '☆';
      });
      Safar.openModal('editFeedback');
    });
  });

  /* live character count */
  const area = document.querySelector('textarea[name="message"][maxlength]');
  const counter = document.querySelector('[data-charcount]');
  if (area && counter) {
    const tick = () => { counter.textContent = `${area.value.length}/${area.maxLength}`; };
    area.addEventListener('input', tick);
    tick();
  }
});
