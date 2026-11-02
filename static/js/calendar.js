// Phones: tap a week heading on the calendar to open or close that week.
// The CSS only hides closed weeks on small screens, so computers always see the full month.
document.querySelectorAll('.cal-week__toggle').forEach(function (button) {
	button.addEventListener('click', function () {
		const week = button.closest('.cal-week');
		const open = week.classList.toggle('is-open');
		button.setAttribute('aria-expanded', open ? 'true' : 'false');
	});
});