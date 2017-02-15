/* === Toggle to show downloads === */
function youAreAPirate (checked) { // eslint-disable-line
  var dlList = document.querySelector('#ImOKWithThat')
  var date = new Date()
  date.setTime(date.getTime() + (365 * 24 * 60 * 60 * 1000))

  if (checked) {
    dlList.style.display = 'block'
    document.cookie = 'WhoAmI=You are a pirate!; expires=' + date.toGMTString() + '; path=/'
  } else {
    dlList.style.display = 'none'
    document.cookie = 'WhoAmI=You are a great person!; expires=' + date.toGMTString() + '; path=/'
  }
}

function checkIfImAPirate () {
  if (readCookie('WhoAmI') === 'You are a pirate!') {
    youAreAPirate(true)
    document.querySelector('#yarr').checked = true
  }
}

checkIfImAPirate()
