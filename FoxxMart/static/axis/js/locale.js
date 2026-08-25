(function () {
  function getCookie(name) {
    var prefix = name + '=';
    return document.cookie.split(';').map(function (part) { return part.trim(); }).reduce(function (value, part) {
      return value || (part.indexOf(prefix) === 0 ? decodeURIComponent(part.slice(prefix.length)) : '');
    }, '');
  }

  if (getCookie('foxxmart_country') || !navigator.geolocation || sessionStorage.getItem('foxxmart_location_attempted')) return;

  sessionStorage.setItem('foxxmart_location_attempted', '1');
  navigator.geolocation.getCurrentPosition(function (position) {
    fetch('/account/region/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      })
    }).then(function (response) {
      if (response.ok) window.location.reload();
    }).catch(function () {
      // The base ZAR price remains visible when location resolution is unavailable.
    });
  }, function () {
    // Declining permission leaves prices in the storefront's ZAR base currency.
  }, { maximumAge: 86400000, timeout: 8000 });
}());
