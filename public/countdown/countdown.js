var episodeList = []
var nextEp = null
var dontTick = false
var tock

window.fetch('https://sug.rocks/countdown/episodes.json')
  .then(function (response) {
    if (response.ok) {
      return response.json()
    } else {
      throw new CodeNotOK(response.status)
    }
  })
  .catch(function (error) {
    document.getElementById('hours').innerHTML = 'Can\'t load shit'
    console.err(error)
  })
  .then(function (episodes) {
    episodes.forEach(
      function (episode) {
        var t = new Date()

        t.setTime(0)
        t.setUTCFullYear(episode['year'])
        t.setUTCMonth(episode['month'] - 1)
        t.setUTCDate(episode['day'])

        t.setUTCHours(episode['hour'])
        t.setUTCMinutes(episode['minute'])

        episode['dateObj'] = t
        episode['dateEnd'] = new Date(t.getTime() + (episode['duration'] * 60 * 1000))

        episodeList.push(episode)
      }
    )

    startClock()
  })

function CodeNotOK (code) {
  this.code = code
  this.message = 'The response code is not OK'
  this.toString = function () {
    return this.message + ': ' + this.code
  }
}

function startClock () {
  new Promise(
    function (resolve, reject) {
      var ts = new Date().getTime()

      var notHiatus = episodeList.some(
        function (episode, index, arr) {
          if (ts < episode['dateEnd'].getTime()) {
            nextEp = episode
            return true
          }
        }
      )

      if (notHiatus) {
        resolve(nextEp)
      } else {
        dontTick = true
        nextEp = null
        document.getElementById('title').innerHTML = 'SU is now in'
        document.getElementById('code').innerHTML = '&nbsp;'
        document.getElementById('hours').innerHTML = 'Hiatus'
        document.getElementById('status').innerHTML = ':('
      }
    }
  ).then(function (nextEp) {
    var status = '&nbsp;'

    if (nextEp['leaked']) {
      status = '(but already leaked)'
    } else if (nextEp['supposed']) {
      status = '(supposed)'
    } else if (nextEp['unknown']) {
      clearCountdown()
      document.getElementById('hours').innerHTML = 'Unknown Date'
      dontTick = true
    } else {
      status = 'until airing on TV'
    }

    document.getElementById('title').innerHTML = nextEp['title']
    document.getElementById('code').innerHTML = ' [' + nextEp['code'] + ']'
    document.getElementById('status').innerHTML = status

    if (!dontTick) {
      // start tock
      tock = setInterval(function () { tick() }, 1000)
    }
  })
}

function clearCountdown () {
  document.getElementById('days').innerHTML = ''
  document.getElementById('minutes').innerHTML = ''
  document.getElementById('seconds').innerHTML = ''
}

function pad (number) {
  if (number < 10) return '0' + number
  return number
}

function getDiff (date) {
  var ts = new Date().getTime()
  var diff = date - ts

  var d
  var days = Math.floor(diff / (24 * 60 * 60 * 1000))
  if (days === 1) {
    d = '1 day '
  } else if (days > 0) {
    d = days + ' days '
  } else {
    d = ''
  }

  diff = diff - days * (24 * 60 * 60 * 1000)
  var hours = Math.floor(diff / (60 * 60 * 1000))

  diff = diff - hours * (60 * 60 * 1000)
  var minutes = Math.floor(diff / (60 * 1000))

  diff = diff - minutes * (60 * 1000)
  var seconds = Math.floor(diff / 1000)

  return {
    d: d,
    h: pad(hours) + ':',
    m: pad(minutes),
    s: ':' + pad(seconds)
  }
}

function formatDate (dateObj) {
  if (typeof Intl !== 'undefined') {
    return dateObj.toLocaleString(navigator.language, {weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'})
  }
  var weekday = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
  var res = weekday[dateObj.getDay()] + '. ' + dateObj.getFullYear() + '-' + pad(dateObj.getMonth() + 1) + '-'
  return res + pad(dateObj.getDate()) + ' ' + pad(dateObj.getHours()) + ':' + pad(dateObj.getMinutes())
}

function tick () {
  var ts = new Date().getTime()

  if (ts > nextEp['dateEnd'].getTime()) {
    clearInterval(tock)
    startClock()
  } else if (ts > nextEp['dateObj'].getTime()) {
    clearCountdown()
    document.getElementById('hours').innerHTML = 'LIVE!'
  } else {
    var diff = getDiff(nextEp['dateObj'])
    document.getElementById('days').innerHTML = diff['d']
    document.getElementById('hours').innerHTML = diff['h']
    document.getElementById('minutes').innerHTML = diff['m']
    document.getElementById('seconds').innerHTML = diff['s']
  }
}

function getList () { // eslint-disable-line no-unused-vars
  if (nextEp == null) {
    window.alert('No new episodes')
    return
  }

  var ts = new Date().getTime()
  var msg = 'New episodes:\n'
  msg += '--------------------------\n\n'

  episodeList.forEach(function (ep) {
    if (ts < ep['dateObj'].getTime()) {
      var diff = getDiff(ep['dateObj'])
      msg += ep['title'] + ' (' + ep['code'] + ')'
      if (!ep['unknown']) {
        msg += '\n' + diff['d'] + diff['h'] + diff['m']
        msg += '\n' + formatDate(ep['dateObj'])
        if (ep['supposed']) {
          msg += '\n(supposed)'
        }
      }
      msg += '\n\n'
    }
  })

  msg += '--------------------------\n'
  msg += 'Sources: Cartoon Network, Screener\n'

  window.alert(msg)
}
