/* global XMLHttpRequest */
function checkRadio () {
  var xhttp = new XMLHttpRequest()

  xhttp.onreadystatechange = function () {
    if (xhttp.readyState === 4 && xhttp.status === 200) {
      var stationJson = JSON.parse(xhttp.responseText).icestats.source
      var musicTitle

      if (stationJson[0]) {
        musicTitle = stationJson[0].title
      } else {
        musicTitle = stationJson.title
      }

      musicTitle = musicTitle.replace('Steven Universe - ', '')
      document.getElementById('np-radio').innerHTML = '<b>Now Playing:</b> ' + musicTitle
    }
  }

  xhttp.open('GET', 'https://radio.sug.rocks/status-json.xsl?' + Math.floor((Math.random() * 99999) + 1), true)
  xhttp.send()
}
checkRadio()
setInterval(checkRadio, 5000)
document.getElementsByTagName('audio')[0].volume = 0.5
