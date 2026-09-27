/*
	Miniport by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

// Hold transitions until the page has loaded (see body.is-preload in main.scss).
// Nav links scroll natively (scroll-behavior in main.scss), so no scroll plugin is needed.
window.addEventListener('load', function () {
	window.setTimeout(function () {
		document.body.classList.remove('is-preload');
	}, 100);
});
