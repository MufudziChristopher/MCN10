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
;
(function (window) {

    'use strict';

    var support = {
            animations: Modernizr.cssanimations
        },
        animEndEventNames = {
            'WebkitAnimation': 'webkitAnimationEnd',
            'OAnimation': 'oAnimationEnd',
            'msAnimation': 'MSAnimationEnd',
            'animation': 'animationend'
        },
        animEndEventName = animEndEventNames[Modernizr.prefixed('animation')],
        onEndAnimation = function (el, callback) {
            var onEndCallbackFn = function (ev) {
                if (support.animations) {
                    if (ev.target != this) return;
                    this.removeEventListener(animEndEventName, onEndCallbackFn);
                }
                if (callback && typeof callback === 'function') {
                    callback.call();
                }
            };
            if (support.animations) {
                el.addEventListener(animEndEventName, onEndCallbackFn);
            } else {
                onEndCallbackFn();
            }
        };

    // from http://www.sberry.me/articles/javascript-event-throttling-debouncing
    function throttle(fn, delay) {
        var allowSample = true;

        return function (e) {
            if (allowSample) {
                allowSample = false;
                setTimeout(function () {
                    allowSample = true;
                }, delay);
                fn(e);
            }
        };
    }


    // sliders - flickity
    var sliders = [].slice.call(document.querySelectorAll('.slider')),
        // array where the flickity instances are going to be stored
        flkties = [],
        // grid element
        grid = document.querySelector('.grid'),
        // isotope instance
        iso,
        // filter ctrls
        filterCtrls = [].slice.call(document.querySelectorAll('#cbp-spmenu-s1 .filter__item')),
        filterSearchInput = document.querySelector('#filter-search-input'),
        filterSearchEmpty = document.querySelector('.filter-search__empty'),
        filterSearchClear = document.querySelector('.filter-search__clear'),
        // cart
        cart = document.querySelector('.cart'),
        cartItems = cart.querySelector('.cart__count');

    function init() {
        // preload images
        imagesLoaded(grid, function () {
            initFlickity();
            initIsotope();
            initEvents();
            classie.remove(grid, 'grid--loading');
        });
    }

    function initFlickity() {
        sliders.forEach(function (slider) {
            var flkty = new Flickity(slider, {
                prevNextButtons: true,
                wrapAround: true,
                cellAlign: 'left',
                contain: true,
                autoPlay: 3500,
                pauseAutoPlayOnHover: true,
                resize: false
            });

            addCarouselIcon(flkty.prevButton, 'chevron-back-outline.svg');
            addCarouselIcon(flkty.nextButton, 'chevron-forward-outline.svg');

            // store flickity instances
            flkties.push(flkty);
        });
    }

    function addCarouselIcon(button, icon) {
        if (!button || !button.element) return;

        var ionIcon = document.createElement('ion-icon');
        ionIcon.className = 'product-carousel__arrow-icon';
        ionIcon.setAttribute('src', '/static/ion-icons/' + icon);
        ionIcon.setAttribute('aria-hidden', 'true');
        button.element.appendChild(ionIcon);
    }

    function initIsotope() {
        iso = new Isotope(grid, {
            isResizeBound: false,
            itemSelector: '.grid__item',
            percentPosition: true,
            masonry: {
                // use outer width of grid-sizer for columnWidth
                columnWidth: '.grid__sizer'
            },
            transitionDuration: '0.6s'
        });
    }

    function initEvents() {
        filterCtrls.forEach(function (filterCtrl) {
            filterCtrl.addEventListener('click', function () {
                classie.remove(filterCtrl.parentNode.querySelector('.filter__item--selected'), 'filter__item--selected');
                classie.add(filterCtrl, 'filter__item--selected');
                iso.arrange({
                    filter: filterCtrl.getAttribute('data-filter')
                });
                recalcFlickities();
                iso.layout();
            });
        });

        if (filterSearchInput && filterSearchEmpty) {
            function searchFilters() {
                var query = filterSearchInput.value.trim().toLowerCase(),
                    matches = 0;

                filterCtrls.forEach(function (filterCtrl) {
                    var isAllOption = filterCtrl.getAttribute('data-filter') === '*',
                        isMatch = isAllOption || filterCtrl.textContent.toLowerCase().indexOf(query) !== -1;

                    filterCtrl.hidden = !isMatch;
                    if (!isAllOption && isMatch) {
                        matches++;
                    }
                });

                filterSearchEmpty.hidden = matches !== 0 || query === '';
                if (filterSearchClear) {
                    filterSearchClear.hidden = query === '';
                }
            }

            filterSearchInput.addEventListener('input', searchFilters);

            if (filterSearchClear) {
                filterSearchClear.addEventListener('click', function () {
                    filterSearchInput.value = '';
                    searchFilters();
                    filterSearchInput.focus();
                });
            }
        }

        // window resize / recalculate sizes for both flickity and isotope/masonry layouts
        window.addEventListener('resize', throttle(function (ev) {
            recalcFlickities()
            iso.layout();
        }, 50));

        // add to cart
		[].slice.call(grid.querySelectorAll('.grid__item')).forEach(function (item) {
            item.querySelector('.action--buy').addEventListener('click', addToCart);
        });
    }

    function addToCart() {
        classie.add(cart, 'cart--animate');
        setTimeout(function () {
            cartItems.innerHTML = Number(cartItems.innerHTML) + 1;
        }, 200);
        onEndAnimation(cartItems, function () {
            classie.remove(cart, 'cart--animate');
        });
    }

    function recalcFlickities() {
        for (var i = 0, len = flkties.length; i < len; ++i) {
            flkties[i].resize();
        }
    }

    init();

})(window);
