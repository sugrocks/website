var episodeList = []
var nextEp = null
var dontTick = false
var tock

// Get our episode list
window.fetch('https://sug.rocks/countdown/episodes.json?' + Math.floor((Math.random() * 10000) + 1))
  .then(function (response) {
    if (response.ok) {
      // If we got the file, parse the json and return it
      return response.json()
    } else {
      // If not OK, tell us
      throw new CodeNotOK(response.status)
    }
  })
  .catch(function (error) {
    // Fuck, what the hell could happen
    document.getElementById('hours').innerHTML = 'Can\'t load shit'
    console.error(error)
  })
  .then(function (episodes) {
    // Parse every entries
    episodes.forEach(
      function (episode) {
        // Create new empty date object
        var t = new Date(0)

        // Set data from the episode entry
        t.setUTCFullYear(episode.year)
        t.setUTCMonth(episode.month - 1)
        t.setUTCDate(episode.day)
        t.setUTCHours(episode.hour)
        t.setUTCMinutes(episode.minute)

        // Add date object to the episode dict
        episode.dateObj = t
        // Add end date
        episode.dateEnd = new Date(t.getTime() + (episode.duration * 60 * 1000))

        // Push to our global array
        episodeList.push(episode)
      }
    )

    // And start the clock
    startClock()
  })

function CodeNotOK (code) {
  // In case something goes wrong
  this.code = code
  this.message = 'The response code is not OK'
  this.toString = function () {
    return this.message + ': ' + this.code
  }
}

function startClock () {
  new Promise(
    function (resolve, reject) {
      // Get current timestamp
      var ts = new Date().getTime()

      // Verifiy if there's something next
      var notHiatus = episodeList.some(
        function (episode, index, arr) {
          if (ts < episode.dateEnd.getTime()) {
            // Save the next upcoming episode and return
            nextEp = episode
            return true
          }
        }
      )

      if (notHiatus) {
        // If there's something, let's continue
        resolve(nextEp)
        document.getElementById('container').classList.remove('hiatus')
      } else {
        // If not, clear everything and stop here
        dontTick = true
        nextEp = null
        var hiatusDiff = new Date().getTime() - episodeList[episodeList.length - 1].dateEnd
        var hiatusDays = Math.floor(hiatusDiff / (24 * 60 * 60 * 1000))
        hiatusDiff = hiatusDiff - hiatusDays * (24 * 60 * 60 * 1000)
        var hiatusHours = Math.floor(hiatusDiff / (60 * 60 * 1000))
        clearCountdown()
        document.getElementById('container').className = 'hiatus'
        document.getElementById('title').innerHTML = 'Finally, Steven now has a'
        document.getElementById('code').innerHTML = ''
        document.getElementById('hours').innerHTML = 'therapist'
        document.getElementById('status').innerHTML = '(It\'s been ' + hiatusDays + ' days and ' + hiatusHours + ' hours.)'
      }
    }
  ).then(function (nextEp) {
    var status = ''

    // Choose our status text
    if (nextEp.leaked) {
      status = '(but already online)'
    } else if (nextEp.supposed) {
      status = '(supposed)'
    } else if (nextEp.unknown) {
      // If it's unknown, clear everything and stop the clock
      clearCountdown()
      document.getElementById('hours').innerHTML = 'Unknown Date'
      dontTick = true
      /*
    } else if (nextEp.app) {
      status = 'on the CN app'
    } else {
      status = 'until airing on TV'
      */
    }

    // Set text (title, episode code and status)
    document.getElementById('title').innerHTML = nextEp.title
    document.getElementById('code').innerHTML = ' [' + nextEp.code + ']'
    document.getElementById('status').innerHTML = status

    if (!dontTick) {
      // first tick
      tick()
      // start tock
      tock = setInterval(function () { tick() }, 1000)
    }
  })
}

function clearCountdown () {
  // Empty the days, minutes and seconds span
  // We don't need to do it on hours, since we always set something to it
  document.getElementById('days').innerHTML = ''
  document.getElementById('minutes').innerHTML = ''
  document.getElementById('seconds').innerHTML = ''
}

function pad (number) {
  // Add leading 0 if needed
  if (number < 10) return '0' + number
  return number
}

function getDiff (date) {
  // Get our timestamp and the difference to the date
  var ts = new Date().getTime()
  var diff = date - ts

  // Get number of days
  var d
  var days = Math.floor(diff / (24 * 60 * 60 * 1000))
  if (days === 1) {
    d = '1 day '
  } else if (days > 0) {
    d = days + ' days '
  } else {
    // If there's no days left, don't display it
    d = ''
  }

  // Get number of hours
  diff = diff - days * (24 * 60 * 60 * 1000)
  var hours = Math.floor(diff / (60 * 60 * 1000))

  // Get number of minutes
  diff = diff - hours * (60 * 60 * 1000)
  var minutes = Math.floor(diff / (60 * 1000))

  // Get number of seconds
  diff = diff - minutes * (60 * 1000)
  var seconds = Math.floor(diff / 1000)

  // Return our values formated
  return {
    d: d,
    h: pad(hours) + ':',
    m: pad(minutes),
    s: ':' + pad(seconds)
  }
}

function formatDate (dateObj) {
  // Format the date to a readable state
  // Use browser language if available
  if (typeof Intl !== 'undefined') {
    return dateObj.toLocaleString(navigator.language, { weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
  }

  // If not available, we do it ourself
  var weekday = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
  var res = weekday[dateObj.getDay()] + '. ' + dateObj.getFullYear() + '-' + pad(dateObj.getMonth() + 1) + '-'
  res += pad(dateObj.getDate()) + ' ' + pad(dateObj.getHours()) + ':' + pad(dateObj.getMinutes())
  return res
}

function tick () {
  // Tick of the tock, get our timestamp first
  var ts = new Date().getTime()

  if (ts > nextEp.dateEnd.getTime()) {
    // If the current episode ended, stop the tock and get the next element
    clearInterval(tock)
    startClock()
  } else if (ts > nextEp.dateObj.getTime()) {
    // If we're past the start time (and we didn't end), display that it's live
    clearCountdown()
    document.getElementById('hours').innerHTML = 'LIVE!'
  } else {
    // Else, get the diff and display it
    var diff = getDiff(nextEp.dateObj)

    document.getElementById('days').innerHTML = diff.d
    document.getElementById('hours').innerHTML = diff.h
    document.getElementById('minutes').innerHTML = diff.m
    document.getElementById('seconds').innerHTML = diff.s
  }
}

function getList () { // eslint-disable-line no-unused-vars
  // Users can request a list
  if (nextEp == null) {
    // Sorry, there's nothing
    window.alert('No new episodes')
    return
  }

  // Get current timestamp
  var ts = new Date().getTime()

  // We'll store the message content here
  var msg = ''

  // Let's get every episodes saved
  episodeList.forEach(function (ep) {
    if (ts < ep.dateObj.getTime()) {
      // If it's not in the past, get the diff
      var diff = getDiff(ep.dateObj)

      // Display title and code
      msg += ep.title + ' (' + ep.code + ')'

      // If date is not unknown, display it
      if (!ep.unknown && !ep.leaked) {
        msg += '\n' + diff.d + diff.h + diff.m
        msg += '\n' + formatDate(ep.dateObj)

        // Add a not if it's supposed
        if (ep.supposed) {
          msg += '\n(supposed)'
        }
      }

      msg += '\n\n'
    }
  })

  // And display it to our user
  window.alert(msg)
}
