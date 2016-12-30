/* global readCookie */
function allowNSFW () { // eslint-disable-line
  var date = new Date()
  date.setTime(date.getTime() + (365 * 24 * 60 * 60 * 1000))
  document.cookie = 'allowNSFW=true; expires=' + date.toGMTString() + '; path=/'

  checkNSFW()
}

function checkNSFW () {
  var status = readCookie('allowNSFW')

  if (status === 'true') {
    var tags = document.getElementsByTagName('link')

    for (var i = 0; i < tags.length; i++) {
      if ((tags[i].rel.indexOf('stylesheet') !== -1) && tags[i].title) {
        if (tags[i].title === 'allowNSFW') {
          tags[i].removeAttribute('disabled')
        }
      }
    }
  }
}

checkNSFW()
