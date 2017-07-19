/* global readCookie */
/* === Jump and open spoilers based on hash === */
function jumpToDl () {
  var jump = window.location.hash.slice(1)

  if (jump !== '') {
    if (jump.slice(-1) === 't') {
      document.querySelector('#preair > .link').click()
    } else if (jump.slice(-1) === 'm') {
      document.querySelector('#individual > .link').click()
    } else if (jump.slice(-1) === 'i') {
      document.querySelector('#itunes > .link').click()
    } else {
      document.querySelector('#comics > .link').click()
    }

    document.getElementById(jump).scrollIntoView()
  }
}

/* === Toggle to show downloads === */
function youAreAPirate (checked) { // eslint-disable-line
  var dlList = document.querySelector('#ImOKWithThat')
  var date = new Date()
  date.setTime(date.getTime() + (365 * 24 * 60 * 60 * 1000))

  if (checked) {
    dlList.style.display = 'block'
    document.cookie = 'WhoAmI=You are a pirate!; expires=' + date.toGMTString() + '; path=/'
    setTimeout(jumpToDl, 1000)
  } else {
    dlList.style.display = 'none'
    document.cookie = 'WhoAmI=You are a great person!; expires=' + date.toGMTString() + '; path=/'
  }
}

/* === Display the downloads on page load if ===
 * === we are recognized as a pirate (Yarr!) === */
function checkIfImAPirate () {
  if (readCookie('WhoAmI') === 'You are a pirate!') {
    youAreAPirate(true)
    document.querySelector('#yarr').checked = true
  }
}

checkIfImAPirate()
