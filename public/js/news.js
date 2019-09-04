/* global XMLHttpRequest */
/* === Display the news bar === */
function checkNews () {
  var notif = document.querySelector('.notif')
  var xhttp = new XMLHttpRequest()

  xhttp.onreadystatechange = function () {
    if (xhttp.readyState === 4 && xhttp.status === 200) {
      if (xhttp.responseText.trim() !== '') {
        notif.innerHTML = xhttp.responseText
        notif.style.display = 'block'
      } else {
        notif.style.display = 'none'
      }
    }
  }

  xhttp.open('GET', 'https://sug.rocks/news.txt?' + Math.floor((Math.random() * 99999) + 1), true)
  xhttp.send()
}

/* === Display the plug (ad) === */
function plugBanner () {
  var linkPlug = document.querySelector('.plug a')
  var deskPlug = document.querySelector('.plug .is-hidden-mobile')
  var mobilePlug = document.querySelector('.plug .is-hidden-tablet')

  var xhttp = new XMLHttpRequest()

  xhttp.onreadystatechange = function () {
    if (xhttp.readyState === 4 && xhttp.status === 200) {
      if (xhttp.responseText.trim() !== '') {
        var plugs = JSON.parse(xhttp.responseText)
        var random = plugs[Math.floor(Math.random() * plugs.length)]
        var picIndex = Math.floor(Math.random() * random.desktop.length)

        linkPlug.href = random.url
        deskPlug.src = random.desktop[picIndex]
        mobilePlug.src = random.mobile[picIndex]
      }
    }
  }

  xhttp.open('GET', 'https://sug.rocks/plugs.json?' + Math.floor((Math.random() * 99999) + 1), true)
  xhttp.send()
}

plugBanner()
checkNews()
setInterval(checkNews, 120000)
