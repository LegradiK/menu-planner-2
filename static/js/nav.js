// Header dropdowns (Recipes, account menu).
// <details> already opens and closes on click/tap without JavaScript;
// this only closes a menu when you open another one, click elsewhere, or press Esc.
(function () {
	const menus = document.querySelectorAll('.nav-menu');

	menus.forEach(function (menu) {
		menu.addEventListener('toggle', function () {
			if (!menu.open) return;
			menus.forEach(function (other) {
				if (other !== menu) other.open = false;
			});
		});
	});

	document.addEventListener('click', function (event) {
		menus.forEach(function (menu) {
			if (menu.open && !menu.contains(event.target)) menu.open = false;
		});
	});

	document.addEventListener('keydown', function (event) {
		if (event.key !== 'Escape') return;
		menus.forEach(function (menu) {
			if (menu.open) {
				menu.open = false;
				menu.querySelector('summary').focus();
			}
		});
	});
})();