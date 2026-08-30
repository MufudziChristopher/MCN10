/**
 * main.js
 * http://www.codrops.com
 *
 * Licensed under the MIT license.
 * http://www.opensource.org/licenses/mit-license.php
 *
 * Copyright 2015, Codrops
 * http://www.codrops.com
 */
(function() {

	var viewEl = document.querySelector('.view'),
		gridEl = viewEl.querySelector('.grid'),
		items = [].slice.call(gridEl.querySelectorAll('.product')),
		basket;

	function collapseNavigationForCompare() {
		var menu = document.querySelector('[data-collapsible-menu]');
		var toggle = document.querySelector('[data-collapsible-menu-toggle]');
		if (!menu || !toggle || menu.classList.contains('is-collapsed')) return;
		menu.classList.add('is-collapsed');
		document.body.classList.add('has-collapsed-menu');
		toggle.setAttribute('aria-expanded', 'false');
	}

	// the compare basket
	function CompareBasket() {
		this.el = document.querySelector('.compare-basket');
		this.compareCtrl = this.el.querySelector('.action--compare');
		this.clearCtrl = this.el.querySelector('.compare-basket__clear');
		this.compareWrapper = document.querySelector('.compare'),
		this.closeCompareCtrl = this.compareWrapper.querySelector('.action--close'),
		this.mobileCollapseCtrl = document.querySelector('.compare__collapse');

		this.itemsAllowed = 5;
		this.totalItems = 0;
		this.items = [];

		// compares items in the compare basket: opens the compare products wrapper
		this.compareCtrl.addEventListener('click', this._compareItems.bind(this));
		this.clearCtrl.addEventListener('click', this.clear.bind(this));
		// close the compare products wrapper
		var self = this;
		this.closeCompareCtrl.addEventListener('click', function() {
			// toggle compare basket
			if (self.totalItems) {
				classie.add(self.el, 'compare-basket--active');
			}
			// animate..
			classie.remove(viewEl, 'view--compare');
		});
		if (this.mobileCollapseCtrl) {
			this.mobileCollapseCtrl.addEventListener('click', function() {
				self.closeCompareCtrl.click();
			});
		}
	}

	CompareBasket.prototype.add = function(item) {
		// check limit
		if( this.isFull() ) {
			return false;
		}

		collapseNavigationForCompare();
		classie.add(item, 'product--selected');

		// create item preview element
		var preview = this._createItemPreview(item);
		// prepend it to the basket
		this.el.insertBefore(preview, this.el.childNodes[0]);
		// insert item
		this.items.push(preview);

		this.totalItems++;
		if( this.isFull() ) {
			classie.add(this.el, 'compare-basket--full');
		}

		classie.add(this.el, 'compare-basket--active');
	};

	CompareBasket.prototype.clear = function() {
		while (this.items.length) {
			var preview = this.items[0];
			var item = items[parseInt(preview.getAttribute('data-idx'), 10)];
			this.remove(item);
		}
	};

	CompareBasket.prototype._createItemPreview = function(item) {
		var self = this;

		var preview = document.createElement('div');
		preview.className = 'product-icon';
		preview.setAttribute('data-idx', items.indexOf(item));

		var removeCtrl = document.createElement('button');
		removeCtrl.className = 'action action--remove';
		removeCtrl.innerHTML = '<ion-icon name="close-circle-outline" aria-hidden="true"></ion-icon><span class="action__text action__text--invisible">Remove product</span>';
		removeCtrl.addEventListener('click', function() {
			self.remove(item);
		});

		var productImageEl = item.querySelector('img.product__image').cloneNode(true);

		preview.appendChild(productImageEl);
		preview.appendChild(removeCtrl);

		var productPriceEl = item.querySelector('.product__price');
		if (productPriceEl) {
			var priceEl = document.createElement('span');
			priceEl.className = 'compare-basket__price';
			priceEl.textContent = productPriceEl.textContent.trim();
			preview.appendChild(priceEl);
			preview.setAttribute('data-price', priceEl.textContent);
		}

		var sourceCartCtrl = item.querySelector('.action--compare-buy.update-cart');
		if (sourceCartCtrl) {
			preview.setAttribute('data-product-id', sourceCartCtrl.dataset.product);
		}

		var productInfo = item.querySelector('.product__info').innerHTML;
		preview.setAttribute('data-info', productInfo);

		return preview;
	};

	CompareBasket.prototype._renderCompareTotal = function() {
		var existingTotal = document.querySelector('.compare__grand-total--viewport');
		if (existingTotal) {
			existingTotal.remove();
		}

		var total = 0;
		var currency = '';
		this.items.forEach(function(preview) {
			var priceText = preview.getAttribute('data-price') || '';
			if (!currency) {
				currency = (priceText.match(/^[^0-9]*/) || [''])[0];
			}
			total += parseFloat(priceText.replace(/[^0-9.,]/g, '').replace(/,/g, '')) || 0;
		});

		var totalEl = document.createElement('p');
		totalEl.className = 'compare__grand-total compare__grand-total--viewport';
		totalEl.textContent = 'Grand Total: ' + currency + total.toLocaleString('en-ZA', {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		});
		// The glass compare overlay uses backdrop-filter, which traps fixed
		// descendants inside its scrolling containing block. Keep the total at
		// the document root so mobile position: fixed remains viewport-fixed.
		document.body.appendChild(totalEl);
	};

	CompareBasket.prototype.remove = function(item) {
		classie.remove(this.el, 'compare-basket--full');
		classie.remove(item, 'product--selected');
		var preview = this.el.querySelector('[data-idx = "' + items.indexOf(item) + '"]');
		this.el.removeChild(preview);
		this.totalItems--;

		var indexRemove = this.items.indexOf(preview);
		this.items.splice(indexRemove, 1);

		if( this.totalItems === 0 ) {
			classie.remove(this.el, 'compare-basket--active');
		}

		// checkbox
		var checkbox = item.querySelector('.action--compare-add > input[type = "checkbox"]');
		if( checkbox.checked ) {
			checkbox.checked = false;
		}
	};

	CompareBasket.prototype._compareItems = function() {
		var self = this;
		collapseNavigationForCompare();
		var filterDrawer = document.getElementById('cbp-spmenu-s1');
		var filterControl = document.getElementById('showLeftPush');

		// The expanded comparison overlay should never compete with the filter drawer.
		if (filterDrawer) {
			classie.remove(filterDrawer, 'cbp-spmenu-open');
		}
		if (filterControl) {
			classie.remove(filterControl, 'active');
		}
		classie.remove(document.body, 'cbp-spmenu-push-toright');

		// remove all previous items inside the compareWrapper element
		[].slice.call(this.compareWrapper.querySelectorAll('div.compare__item')).forEach(function(item) {
			self.compareWrapper.removeChild(item);
		});

		for(var i = 0; i < this.totalItems; ++i) {
			var preview = this.items[i];
			var sourceItem = items[parseInt(preview.getAttribute('data-idx'), 10)];
			var compareItemWrapper = document.createElement('div');
			compareItemWrapper.className = 'compare__item';

			var compareItemEffectEl = document.createElement('div');
			compareItemEffectEl.className = 'compare__effect';

			compareItemEffectEl.innerHTML = preview.getAttribute('data-info');

			var productId = preview.getAttribute('data-product-id');
			if (productId) {
				var addToCartCtrl = document.createElement('button');
				addToCartCtrl.className = 'compare__add-to-cart';
				addToCartCtrl.type = 'button';
				addToCartCtrl.innerHTML = '<ion-icon name="cart-outline" aria-hidden="true"></ion-icon><span>Add to Cart</span>';
				addToCartCtrl.addEventListener('click', (function(selectedProductId) {
					return function() {
						if (user === 'AnonymousUser') {
							addCookieItem(selectedProductId, 'add');
						} else {
							updateUserOrder(selectedProductId, 'add');
						}
					};
				})(productId));
				compareItemEffectEl.appendChild(addToCartCtrl);
			}

			var removeCompareCtrl = document.createElement('button');
			removeCompareCtrl.className = 'compare__remove';
			removeCompareCtrl.type = 'button';
			removeCompareCtrl.setAttribute('aria-label', 'Remove product from comparison');
			removeCompareCtrl.innerHTML = '<ion-icon name="close-circle-outline" aria-hidden="true"></ion-icon>';
			removeCompareCtrl.addEventListener('click', (function(itemToRemove, wrapperToRemove) {
				return function() {
					self.remove(itemToRemove);
					wrapperToRemove.remove();
					self._renderCompareTotal();
					if (self.totalItems === 0) {
						classie.remove(viewEl, 'view--compare');
					}
				};
			})(sourceItem, compareItemWrapper));
			compareItemWrapper.appendChild(removeCompareCtrl);
			compareItemWrapper.appendChild(compareItemEffectEl);

			this.compareWrapper.insertBefore(compareItemWrapper, this.compareWrapper.childNodes[0]);
		}

		this._renderCompareTotal();

		setTimeout(function() {
			// toggle compare basket
			classie.remove(self.el, 'compare-basket--active');
			// animate..
			classie.add(viewEl, 'view--compare');
		}, 25);
	};

	CompareBasket.prototype.isFull = function() {
		return this.totalItems === this.itemsAllowed;
	};

	CompareBasket.prototype.showFullTooltip = function(item) {
		var compareControl = item.querySelector('.action--compare-add');
		if (!compareControl) return;

		compareControl.setAttribute('data-tooltip', 'Remove one or more items.');
		classie.add(compareControl, 'compare-limit-reached');
		clearTimeout(compareControl.fullTooltipTimeout);
		compareControl.fullTooltipTimeout = setTimeout(function() {
			classie.remove(compareControl, 'compare-limit-reached');
		}, 3500);
	};

	function init() {
		// initialize an empty basket
		basket = new CompareBasket();
		initEvents();
	}

	function initEvents() {
		items.forEach(function(item) {
			var checkbox = item.querySelector('.action--compare-add > input[type = "checkbox"]');
			checkbox.checked = false;

			// ctrl to add to the "compare basket"
			checkbox.addEventListener('click', function(ev) {
				if( ev.target.checked ) {
				if( basket.isFull() ) {
					ev.preventDefault();
					basket.showFullTooltip(item);
					return false;
					}
					basket.add(item);
				}
				else {
					basket.remove(item);
				}
			});
		});
	}

	init();

})();
