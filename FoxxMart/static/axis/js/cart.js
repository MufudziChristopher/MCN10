var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
  updateBtns[i].addEventListener('click', function(){
    var productId = this.dataset.product
    var action = this.dataset.action
    console.log('productId:', productId, 'Action:', action)
    console.log('USER:', user)

    if (user == 'AnonymousUser'){
      addCookieItem(productId, action)
    }else{
      updateUserOrder(productId, action)
    }
  })
}

function updateUserOrder(productId, action, quantity){
  console.log('User is authenticated, sending data...')
    var url = '/3rdAxis/api/v1/cart/items/'

    fetch(url, {
      method:'POST',
      headers:{
        'Content-Type':'application/json',
        'X-CSRFToken':csrftoken,
      },
      body:JSON.stringify({'productId':productId, 'action':action, 'quantity':quantity})
    })
    .then((response) => {
       return response.json();
    })
    .then((data) => {
        location.reload()
    });
}

function addCookieItem(productId, action, quantity){
  console.log('User is not authenticated')

  if (action == 'add'){
    if (cart[productId] == undefined){
    cart[productId] = {'quantity':1}

    }else{
      cart[productId]['quantity'] += 1
    }
  }

  if (action == 'remove'){
    cart[productId]['quantity'] -= 1

    if (cart[productId]['quantity'] <= 0){
      console.log('Item should be deleted')
      delete cart[productId];
    }
  }

  if (action == 'cancel'){
    console.log('Item should be deleted')
    delete cart[productId];
  }

  if (action == 'set'){
    var requestedQuantity = parseInt(quantity, 10)
    if (Number.isNaN(requestedQuantity) || requestedQuantity <= 0){
      delete cart[productId];
    } else {
      cart[productId] = {'quantity': requestedQuantity}
    }
  }
  console.log('CART:', cart)
  document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"

  location.reload()
}

var quantityInputs = document.getElementsByClassName('cart-quantity-input')

function quantityWarningKey(productId) {
  return 'axis-cart-quantity-warning-' + productId
}

function saveQuantityWarning(productId, message) {
  sessionStorage.setItem(quantityWarningKey(productId), message)
}

function showQuantityWarnings() {
  var warnings = document.getElementsByClassName('cart-quantity-warning')

  for (var warningIndex = 0; warningIndex < warnings.length; warningIndex++) {
    var warning = warnings[warningIndex]
    var key = quantityWarningKey(warning.dataset.product)
    var message = sessionStorage.getItem(key)

    if (message) {
      warning.textContent = message
      sessionStorage.removeItem(key)
    }
  }
}

function commitQuantityInput(input) {
    var quantity = parseInt(input.value, 10)
    var maximum = parseInt(input.max, 10)

    if (Number.isNaN(quantity)) {
      input.value = input.defaultValue
      return
    }

    if (quantity > maximum) {
      saveQuantityWarning(input.dataset.product, 'Only ' + maximum + ' left.')
    }

    quantity = Math.max(0, Math.min(quantity, maximum))
    input.value = quantity

    if (user == 'AnonymousUser'){
      addCookieItem(input.dataset.product, 'set', quantity)
    } else {
      updateUserOrder(input.dataset.product, 'set', quantity)
    }
}

for (var quantityInputIndex = 0; quantityInputIndex < quantityInputs.length; quantityInputIndex++) {
  var quantityInput = quantityInputs[quantityInputIndex]

  // Number-input spinner arrows emit an input event. Debouncing means that a
  // quick series of clicks sends only the final quantity to the cart endpoint.
  quantityInput.addEventListener('input', function(){
    var input = this
    window.clearTimeout(input.quantityUpdateTimer)
    input.quantityUpdateTimer = window.setTimeout(function () {
      commitQuantityInput(input)
    }, 250)
  })

  // Keep keyboard entry and browser implementations that only fire change
  // working, while avoiding a duplicate request after an arrow click.
  quantityInput.addEventListener('change', function(){
    window.clearTimeout(this.quantityUpdateTimer)
    commitQuantityInput(this)
  })

  quantityInput.addEventListener('keydown', function(event){
    if (event.key === 'Enter') {
      event.preventDefault()
      this.blur()
    }
  })
}

showQuantityWarnings()

function updateQuickCartActionVisibility() {
  var quickCart = document.getElementById('cbp-spmenu-s2')
  if (!quickCart) return

  quickCart.classList.toggle(
    'quick-cart--scrollable',
    quickCart.scrollHeight > quickCart.clientHeight + 1
  )
}

window.addEventListener('load', updateQuickCartActionVisibility)
window.addEventListener('resize', updateQuickCartActionVisibility)

var quickCartToggle = document.getElementById('showRightPush')
if (quickCartToggle) {
  quickCartToggle.addEventListener('click', function(){
    window.setTimeout(updateQuickCartActionVisibility, 350)
  })
}
