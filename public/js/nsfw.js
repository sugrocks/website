/* global readCookie */
function allowNSFW () { // eslint-disable-line
  var date = new Date()
  date.setTime(date.getTime() + (365 * 24 * 60 * 60 * 1000))
  document.cookie = 'allowNSFW=true; expires=' + date.toGMTString() + '; path=/'

  checkNSFW()

  /* NOTE:
   * Firefox is retarted and doesn't apply the styles, so remove them instantly inline.
   * This will be the case only once for other browers where it works.
   * Users may need to click on the warnings every time they load the page if they're using FF.
   */
  var warns = document.querySelectorAll('.red-warning')
  for (var i = 0; i < warns.length; i++) {
    warns[i].style.display = 'none'
  }

  var pics = document.querySelectorAll('.red-image')
  for (var j = 0; j < pics.length; j++) {
    pics[j].style.display = 'inherit'
  }
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
