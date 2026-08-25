(function () {
  'use strict';

  function getCookie(name) {
    var prefix = name + '=';
    return document.cookie.split(';').map(function (cookie) { return cookie.trim(); }).reduce(function (value, cookie) {
      return value || (cookie.indexOf(prefix) === 0 ? decodeURIComponent(cookie.slice(prefix.length)) : '');
    }, '');
  }

  function saveGuestCart(productId, action, size, quantity) {
    var cart = JSON.parse(getCookie('cart') || '{}');
    var item = cart[productId] || { quantity: 0 };
    if (size) item.size = size;
    if (action === 'add') item.quantity += 1;
    if (action === 'remove') item.quantity -= 1;
    if (action === 'cancel') item.quantity = 0;
    if (action === 'set') item.quantity = Math.max(0, Number(quantity) || 0);
    if (item.quantity > 0) cart[productId] = item;
    else delete cart[productId];
    document.cookie = 'cart=' + JSON.stringify(cart) + ';path=/';
    window.location.reload();
  }

  document.querySelectorAll('.update-cart').forEach(function (button) {
    button.addEventListener('click', function () {
      var productId = button.dataset.product;
      var action = button.dataset.action;
      var size = button.dataset.size;
      if (window.user === 'AnonymousUser') {
        saveGuestCart(productId, action, size);
        return;
      }

      fetch('/TheCollective/update_item/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ productId: productId, action: action, size: size })
      }).then(function (response) {
        if (!response.ok) throw new Error('Unable to update cart');
        return response.json();
      }).then(function () {
        window.location.reload();
      }).catch(function () {
        window.location.href = '/account/login/?next=/TheCollective/cart/';
      });
    });
  });

  document.querySelectorAll('.collective-cart-quantity').forEach(function (input) {
    input.addEventListener('change', function () {
      var quantity = Math.max(0, Math.min(Number(input.value) || 0, Number(input.max)));
      input.value = quantity;
      var productId = input.dataset.product;
      var size = input.dataset.size;

      if (window.user === 'AnonymousUser') {
        saveGuestCart(productId, 'set', size, quantity);
        return;
      }

      fetch('/TheCollective/update_item/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ productId: productId, action: 'set', size: size, quantity: quantity })
      }).then(function (response) {
        if (!response.ok) throw new Error('Unable to update cart');
        return response.json();
      }).then(function () {
        window.location.reload();
      }).catch(function () {
        window.location.href = '/account/login/?next=/TheCollective/cart/';
      });
    });
  });

  document.querySelectorAll('.collective-size-option').forEach(function (option) {
    option.addEventListener('click', function () {
      var details = option.closest('.content__item');
      details.querySelectorAll('.collective-size-option').forEach(function (button) {
        button.classList.toggle('is-selected', button === option);
        button.setAttribute('aria-pressed', String(button === option));
      });
      var addButton = details.querySelector('.update-cart');
      addButton.dataset.size = option.dataset.size;
      addButton.disabled = false;
    });
  });
}());
