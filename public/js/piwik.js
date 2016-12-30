var _paq = _paq || []
// tracker methods like "setCustomDimension" should be called before "trackPageView"
_paq.push(['setCookieDomain', '*.sug.rocks'])
_paq.push(['setDomains', ['*.sug.rocks', '*.www.sug.rocks']])
_paq.push(['trackPageView'])
_paq.push(['enableLinkTracking'])
;(function () {
  var u = 'https://piwik.sug.rocks/'
  _paq.push(['setTrackerUrl', u + 'piwik.php'])
  _paq.push(['setSiteId', '1'])
  var d = document
  var g = d.createElement('script')
  var s = d.getElementsByTagName('script')[0]
  g.type = 'text/javascript'
  g.async = true
  g.defer = true
  g.src = u + 'piwik.js'
  s.parentNode.insertBefore(g, s)
})()
