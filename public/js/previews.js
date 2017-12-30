function parseDate (ts) {
  let dobj = new Date(ts * 1000)

  return dobj.toLocaleDateString(
    'en-US',
    {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric'
    }
  )
}

function getPreviews () {
  let div = document.querySelector('.the-stuff')

  window.fetch('https://api.ctoon.network/previews/shows/8')
    .then(data => {
      return data.json()
    })
    .then(json => {
      json.forEach(j => {
        let s = document.createElement('div')
        s.setAttribute('class', 'spoiler spoiler-default spoiler-state-collapsed')
        s.setAttribute('data-connection', 'A')
        s.setAttribute('data-toggle-placement', 'top')
        s.setAttribute('data-toggle-text', j['title'] + (j['airdate'] ? '&nbsp- <small>Air date: ' + parseDate(j['airdate']) + '</small>' : ''))

        let sc = document.createElement('div')
        sc.setAttribute('class', 'spoiler-content')

        let scb = document.createElement('blockquote')
        scb.innerHTML = '<p>' + j['description'] + '</p>'

        sc.appendChild(scb)

        j['videos'].forEach(v => {
          let vd = document.createElement('video')
          vd.src = v
          vd.setAttribute('controls', 'true')
          vd.setAttribute('preload', 'none')
          vd.setAttribute('poster', 'https://proxy.sug.rocks/' + j['images'][0])

          sc.appendChild(vd)
          sc.appendChild(document.createElement('br'))
        })

        j['images'].forEach(i => {
          let a = document.createElement('a')
          a.setAttribute('target', '_blank')
          a.setAttribute('href', i)

          let img = document.createElement('img')
          img.setAttribute('data-src', 'https://proxy.sug.rocks/400x/' + i)
          img.setAttribute('class', 'screenleak lazyload')

          a.appendChild(img)
          sc.appendChild(a)
        })

        s.appendChild(sc)
        div.appendChild(s)
      })

      window.loadSpoilers(window, document)
    })
}

getPreviews()
