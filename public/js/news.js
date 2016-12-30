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

checkNews()
setInterval(checkNews, 120000)
