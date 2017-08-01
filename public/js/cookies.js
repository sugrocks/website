window.addEventListener('load', function () {
  window.cookieconsent.initialise({
    palette: {
      popup: {
        background: '#d6daf0',
        text: '#111111'
      },
      button: {
        background: '#35b214',
        text: '#ffffff'
      }
    },
    theme: 'edgeless',
    position: 'bottom-right',
    type: 'opt-out',
    law: {
      regionalLaw: true
    },
    location: {
      services: ['ipinfo', 'maxmind']
    },
    onStatusChange: function (status) {
      if (this.options.type === 'opt-out' && !this.hasConsented()) {
        window.open('https://piwik.sug.rocks/index.php?module=CoreAdminHome&action=optOut&language=en')
      }
    }
  })
})
