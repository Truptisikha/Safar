/* Console helpers: table search, sorting, and the edit modals. */

document.addEventListener('DOMContentLoaded', () => {
  /* filter any table marked data-searchable */
  document.querySelectorAll('[data-search-for]').forEach((box) => {
    const table = document.querySelector(box.dataset.searchFor);
    if (!table) return;
    box.addEventListener('input', () => {
      const term = box.value.toLowerCase().trim();
      let shown = 0;
      table.querySelectorAll('tbody tr').forEach((row) => {
        const hit = row.textContent.toLowerCase().includes(term);
        row.style.display = hit ? '' : 'none';
        if (hit) shown += 1;
      });
      const note = document.querySelector('[data-search-count]');
      if (note) note.textContent = shown ? `${shown} shown` : 'No matches';
    });
  });

  /* click a th[data-sort] to sort that column */
  document.querySelectorAll('th[data-sort]').forEach((th) => {
    th.style.cursor = 'pointer';
    let ascending = true;
    th.addEventListener('click', () => {
      const table = th.closest('table');
      const body = table.querySelector('tbody');
      const index = [...th.parentElement.children].indexOf(th);
      const numeric = th.dataset.sort === 'number';

      [...body.querySelectorAll('tr')]
        .sort((a, b) => {
          const x = a.children[index].textContent.trim();
          const y = b.children[index].textContent.trim();
          const result = numeric
            ? parseFloat(x.replace(/[^\d.-]/g, '') || 0) - parseFloat(y.replace(/[^\d.-]/g, '') || 0)
            : x.localeCompare(y);
          return ascending ? result : -result;
        })
        .forEach((row) => body.appendChild(row));

      ascending = !ascending;
    });
  });

  /* fill the edit modal from the row's data attributes */
  document.querySelectorAll('[data-edit]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const modalId = btn.dataset.edit;
      const form = document.querySelector(`#${modalId} form`);
      form.action = btn.dataset.action;

      Object.entries(btn.dataset).forEach(([key, value]) => {
        if (key === 'edit' || key === 'action') return;
        const field = form.querySelector(`[name="${key}"]`);
        if (field) field.value = value;
      });

      Safar.openModal(modalId);
    });
  });
});
