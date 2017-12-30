var compressor = require('node-minify')
var ora = require('ora')

function minifyJs (file) {
  var spin = ora(file).start()

  compressor.minify({
    compressor: 'gcc',
    input: file,
    output: file.replace('.js', '.min.js'),
    callback: function (err, min) {
      if (err) {
        spin.fail()
        console.error(err + '\n')
      } else {
        spin.succeed()
      }
    }
  })
}

minifyJs('public/js/cookies.js')
minifyJs('public/js/dl.js')
minifyJs('public/js/menu.js')
minifyJs('public/js/news.js')
minifyJs('public/js/nsfw.js')
minifyJs('public/js/radio.js')
minifyJs('public/js/spoiler.js')
minifyJs('public/js/previews.js')
minifyJs('public/js/theme.js')
minifyJs('public/js/threads.js')
minifyJs('public/countdown/countdown.js')
