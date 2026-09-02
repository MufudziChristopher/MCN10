(() => {
	'use strict';

	document.querySelectorAll('[data-collapsible-menu]').forEach((menu) => {
		const content = menu.querySelector('.collapsible-menu__content');
		const toggle = menu.querySelector('[data-collapsible-menu-toggle]') ||
			(content?.id ? document.querySelector(`[data-collapsible-menu-toggle][aria-controls="${content.id}"]`) : null);
		if (!toggle) return;

		let openedManually = false;
		let lastScrollY = window.scrollY;
		let suppressScrollUntil = 0;
		const collapseAfter = Number(menu.dataset.collapseAfter || 96);
		const startsCollapsed = menu.dataset.startCollapsed === 'true' ||
			(menu.dataset.startCollapsed === 'mobile' && window.matchMedia('(max-width: 60em)').matches);

		const setCollapsed = (collapsed) => {
			menu.classList.toggle('is-collapsed', collapsed);
			document.body.classList.toggle('has-collapsed-menu', collapsed);
			toggle.setAttribute('aria-expanded', String(!collapsed));
		};

		const onScroll = () => {
			/* Expanding the sticky header can cause browser scroll anchoring. That
			 * is layout housekeeping, not an instruction to immediately close it. */
			if (performance.now() < suppressScrollUntil) {
				lastScrollY = window.scrollY;
				return;
			}

			const currentScrollY = window.scrollY;
			const moved = Math.abs(currentScrollY - lastScrollY) > 4;

			/* Keep the menu collapsed throughout the page instead of repeatedly
			 * crossing the threshold as the sticky header changes height. */
			if (currentScrollY > collapseAfter) {
				openedManually = false;
				setCollapsed(true);
			} else if (moved) {
				openedManually = false;
			}
			lastScrollY = currentScrollY;
		};

		toggle.addEventListener('click', () => {
			openedManually = menu.classList.contains('is-collapsed');
			if (openedManually && window.matchMedia('(max-width: 60em)').matches) {
				document.querySelectorAll('.product-quick-cart[open]').forEach((quickCart) => {
					quickCart.removeAttribute('open');
				});
				document.querySelectorAll('#cbp-spmenu-s1.cbp-spmenu-open, #cbp-spmenu-s2.cbp-spmenu-open').forEach((drawer) => {
					drawer.classList.remove('cbp-spmenu-open');
				});
				document.body.classList.remove('cbp-spmenu-push-toright', 'cbp-spmenu-push-toleft');
			}
			suppressScrollUntil = performance.now() + 500;
			setCollapsed(!openedManually);
		});

		/* On phones, the Quick Cart and navigation should never compete for
		 * the same limited screen space. */
		document.querySelectorAll('.product-quick-cart').forEach((quickCart) => {
			quickCart.addEventListener('toggle', () => {
				if (quickCart.open && window.matchMedia('(max-width: 60em)').matches) {
					openedManually = false;
					setCollapsed(true);
				}
			});
		});

		window.addEventListener('scroll', onScroll, { passive: true });

		/* Product details uses Locomotive Scroll, which animates its own
		 * container instead of changing window.scrollY. */
		if (document.querySelector('[data-scroll-container]')) {
			let touchStartY = 0;
			const collapseForVirtualScroll = () => {
				openedManually = false;
				setCollapsed(true);
			};

			document.addEventListener('wheel', (event) => {
				if (event.deltaY > 4) collapseForVirtualScroll();
			}, { passive: true });
			document.addEventListener('touchstart', (event) => {
				touchStartY = event.touches[0]?.clientY || 0;
			}, { passive: true });
			document.addEventListener('touchend', (event) => {
				const endY = event.changedTouches[0]?.clientY || touchStartY;
				if (touchStartY - endY > 8) collapseForVirtualScroll();
			}, { passive: true });
		}
		/* Honour the template's initial state before responding to scroll events. */
		setCollapsed(startsCollapsed);
		onScroll();
	});
})();
