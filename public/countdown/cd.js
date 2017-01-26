var episodes = []
var timeObj, episodeIndex, timestamp

function prep () {
  episodes.sort(function (a, b) { return a.time - b.time })
  for (var i = 0; i < episodes.length; i++) {
    if ((i + 1) < episodes.length && (episodes[(i + 1)].time - episodes[i].time) <= (4 * 60 * 60 * 1000)) {
      episodes[i].timefollow = true
    }
    for (var j = (i + 1); j < episodes.length && episodes[i].timefunc === 'eastern' &&
      (episodes[j].time - episodes[i].time) <= (3 * 7 * 24 * 60 * 60 * 1000); j++) {
      if (episodes[i].timefunc === episodes[j].timefunc) {
        if (episodes[i].offsetdiff !== episodes[j].offsetdiff) {
          episodes[j].dstchange = true
        }
        break
      }
    }
  }
}

function getEpIndex (timestamp) { // eslint-disable-line no-unused-vars
  for (var i = 0; i < episodes.length; i++) {
    if (timestamp < (episodes[i].time + episodes[i].length * 60000)) return i
  }
  return false
}

function pad (number) {
  if (number < 10) return '0' + number
  return number
}

function getFormatedDate (dateObj) {
  if (typeof Intl !== 'undefined') {
    return dateObj.toLocaleString(navigator.language, {weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'})
  }
  var weekday = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
  var res = weekday[dateObj.getDay()] + '. ' + dateObj.getFullYear() + '-' + pad(dateObj.getMonth() + 1) + '-'
  return res + pad(dateObj.getDate()) + ' ' + pad(dateObj.getHours()) + ':' + pad(dateObj.getMinutes())
}

function addEpisode (desc, name, timefunc, year, month, date, hours, minutes, length, leaked, unknown) { // eslint-disable-line no-unused-vars
  var episode = {}
  episode.desc = desc
  episode.name = name
  episode.length = length
  episode.timefunc = timefunc
  var foreigntime = this[timefunc](year, month, date, hours, minutes)
  episode.time = foreigntime.time
  var ltdateObj = new Date(episode.time)
  episode.offsetdiff = foreigntime.offset - ltdateObj.getTimezoneOffset()
  episode.ltdate = getFormatedDate(ltdateObj)
  episode.leaked = leaked
  episode.unknown = unknown
  episode.timefollow = false
  episode.dstchange = false

  episodes.push(episode)
}

function getEpisodeCount (episodeIndex, timestamp) {
  var diff = episodes[episodeIndex].time - timestamp
  if (diff <= 0) return {days: '0', hours: '00', minutes: '00', seconds: '00'}

  var days = Math.floor(diff / (24 * 60 * 60 * 1000))
  diff = diff - days * (24 * 60 * 60 * 1000)

  var hours = Math.floor(diff / (60 * 60 * 1000))
  diff = diff - hours * (60 * 60 * 1000)

  var minutes = Math.floor(diff / (60 * 1000))
  diff = diff - minutes * (60 * 1000)

  var seconds = Math.floor(diff / 1000)

  return {days: days, hours: pad(hours), minutes: pad(minutes), seconds: pad(seconds), data: episodes[episodeIndex]}
}

function episodeList () { // eslint-disable-line no-unused-vars
  if (episodeIndex === false) {
    window.alert('No Episodes')
    return
  }

  var next = 'New episodes:\n--------------------------\n\n'
  for (var i = episodeIndex; i < episodes.length && i < episodeIndex + 5; i++) {
    var count = ''
    if (episodes[i].time - timestamp <= 0) {
      count = '>>'
    } else {
      var countObj = getEpisodeCount(i, timestamp)
      var suffix = (episodes[i].dstchange ? ' *' : '')
      if (episodes[i].unknown !== 1) {
        count = 'in ' + countObj.days + 'd ' + countObj.hours + ':' + countObj.minutes + ':' + countObj.seconds
        count += '\n' + episodes[i].ltdate
      }
      next += '[' + episodes[i].desc + '] ' + episodes[i].name + '\n' + count + suffix + '\n\n'
    }
  }
  if (episodes.length > 5) {
    next += 'And more to come!\n\n'
  }
  next += '---\nSources: misseps, Derpy News and Cartoon Network'

  window.alert(next)
}

function eastern (year, month, date, hours, minutes) { // eslint-disable-line no-unused-vars
  month--
  var utc = Date.UTC(year, month, date, hours + 5, minutes, 0, 0)
  var d = new Date(utc)

  var startDST = new Date(Date.UTC(year, 2, 1, 2 + 5, 0, 0, 0))
  var endDST = new Date(Date.UTC(year, 10, 1, 2 + 4, 0, 0, 0))
  var dayDST = startDST.getUTCDay()
  if (dayDST !== 0) {
    startDST.setUTCDate(15 - dayDST)
  } else {
    endDST.setUTCDate(1)
  }

  if (d >= startDST && d < endDST) {
    return {time: utc - 3600000, offset: 4 * 60} // dst
  } else {
    return {time: utc, offset: 5 * 60}
  }
}

function utc (year, month, date, hours, minutes) { // eslint-disable-line no-unused-vars
  month--
  var utc = Date.UTC(year, month, date, hours, minutes, 0, 0)
  return {time: utc, offset: 0}
}

function countdown () {
  timeObj = new Date()
  timestamp = timeObj.getTime()

  episodeIndex = getEpIndex(timestamp)

  if (episodeIndex === false) {
    document.getElementById('container').className = 'hiatus'
    document.getElementById('name').innerHTML = 'Next air date unknown'
    document.getElementById('desc').innerHTML = ''
    document.getElementById('days').innerHTML = ''
    document.getElementById('hours').innerHTML = 'Hiatus?'
    document.getElementById('minutes').innerHTML = ''
    document.getElementById('seconds').innerHTML = ''
    document.getElementById('status').innerHTML = '<span class="spoiler">RIP</span>'
    return
  }

  var diff = episodes[episodeIndex].time - timestamp
  if (diff <= 0 && !countdown.running) {
    document.getElementById('container').className = 'live'
    document.getElementById('name').innerHTML = 'New Episode'
    document.getElementById('desc').innerHTML = ''
    document.getElementById('days').innerHTML = ''
    document.getElementById('hours').innerHTML = '>LIVE'
    document.getElementById('minutes').innerHTML = ''
    document.getElementById('seconds').innerHTML = ''
    document.getElementById('status').innerHTML = 'on Cartoon Network'
    countdown.running = true
  } else if (diff > 0) {
    countdown.running = false
    var countObj = getEpisodeCount(episodeIndex, timestamp)
    document.getElementById('container').className = 'unknown'
    document.getElementById('name').innerHTML = countObj.data.name
    document.getElementById('desc').innerHTML = ' [' + countObj.data.desc + ']'
    if (countObj.data.unknown === 1) {
      document.getElementById('days').innerHTML = ''
      document.getElementById('hours').innerHTML = 'Unknown Date'
      document.getElementById('minutes').innerHTML = ''
      document.getElementById('seconds').innerHTML = ''
    } else {
      if (countObj.days !== 0) document.getElementById('days').innerHTML = countObj.days + 'd '
      document.getElementById('hours').innerHTML = countObj.hours + ':'
      document.getElementById('minutes').innerHTML = countObj.minutes + ':'
      document.getElementById('seconds').innerHTML = countObj.seconds
    }
    document.getElementById('status').innerHTML = (countObj.data.leaked ? '(but already leaked)' : 'until airing on TV')
  }

  setTimeout(countdown, 1000)
}

window.onload = function () {
  console.log('Hello curious guy!')
  prep()
  countdown()
}
