/* === Manage if we're using the light or dark theme === */
// Read cookie
function readCookie (name) {
  var nameEQ = name + '='
  var ca = document.cookie.split(';')

  for (var i = 0; i < ca.length; i++) {
    var c = ca[i]

    while (c.charAt(0) === ' ') {
      c = c.substring(1, c.length)
    }

    if (c.indexOf(nameEQ) === 0) {
      return c.substring(nameEQ.length, c.length)
    }
  }

  return null
}

// Disable/enable styles from selection
function applyStyle (toggleS) {
  var tags = document.getElementsByTagName('link')

  for (var i = 0; i < tags.length; i++) {
    if ((tags[i].rel.indexOf('stylesheet') !== -1) && tags[i].title) {
      if (tags[i].title === 'dark') {
        tags[i].disabled = toggleS
      }

      if (tags[i].title === 'light') {
        tags[i].disabled = !toggleS
      }
    }
  }
}

// Toggle function
function toggleDark () { // eslint-disable-line
  var toggleS
  var status = readCookie('dark')

  if (status !== 'enabled') {
    status = 'enabled'
    toggleS = false
  } else {
    status = 'disabled'
    toggleS = true
  }

  var date = new Date()
  date.setTime(date.getTime() + (365 * 24 * 60 * 60 * 1000))
  document.cookie = 'dark=' + status + '; expires=' + date.toGMTString() + '; path=/'

  applyStyle(toggleS)
}

// Check cookie and apply
function checkStyle () {
  var toggleS
  var status = readCookie('dark')

  if (status !== 'enabled') {
    toggleS = true
  } else {
    toggleS = false
  }

  applyStyle(toggleS)
}

checkStyle()
