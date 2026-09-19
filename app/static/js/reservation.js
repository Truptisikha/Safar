/* Live seat availability and booking without a page reload. */

async function refreshAvailability(card) {
  const routeId = card.dataset.routeId;
  const dateInput = card.querySelector('input[name="travel_date"]');
  const readout = card.querySelector('[data-seats-left]');
  const bar = card.querySelector('.seat-bar i');
  const seatInput = card.querySelector('input[name="seats"]');
  const submit = card.querySelector('button[type="submit"]');
  if (!dateInput?.value || !readout) return;

  readout.textContent = 'Checking…';
  const res = await Safar.request(
    `/api/routes/${routeId}/availability?date=${dateInput.value}`
  );

  if (!res.ok) { readout.textContent = res.error; return; }

  const free = res.seats_available;
  const total = Number(card.dataset.totalSeats || free || 1);
  readout.textContent = free ? `${free} of ${total} seats left` : 'Sold out for this date';

  if (bar) {
    bar.style.width = Math.round((free / total) * 100) + '%';
    bar.parentElement.classList.toggle('tight', free <= total * 0.2);
  }
  if (seatInput) seatInput.max = Math.max(free, 1);
  if (submit) submit.disabled = free === 0;

  updateTotal(card, res.fare);
}

function updateTotal(card, fare) {
  const seats = Number(card.querySelector('input[name="seats"]')?.value || 1);
  const slot = card.querySelector('[data-total]');
  const unit = Number(fare ?? card.dataset.fare ?? 0);
  if (slot) slot.textContent = Safar.money(unit * seats);
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-route-id]').forEach((card) => {
    const dateInput = card.querySelector('input[name="travel_date"]');
    const seatInput = card.querySelector('input[name="seats"]');

    dateInput?.addEventListener('change', () => refreshAvailability(card));
    seatInput?.addEventListener('input', () => updateTotal(card));

    if (dateInput?.value) refreshAvailability(card);
    else updateTotal(card);
  });
});
