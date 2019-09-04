const fs = require('fs')
const ora = require('ora')
const Terser = require('terser')

const files = [
  'public/js/cookies.js',
  'public/js/dl.js',
  'public/js/menu.js',
  'public/js/news.js',
  'public/js/nsfw.js',
  'public/js/radio.js',
  'public/js/spoiler.js',
  'public/js/previews.js',
  'public/js/theme.js',
  'public/js/threads.js',
  'public/countdown/countdown.js'
]

files.forEach(f => {
  const spin = ora(f).start()

  fs.readFile(f, 'utf8', (err, data) => {
    if (err) {
      spin.fail()
      console.error('\n' + err + '\n')
    } else {
      const min = Terser.minify(data)

      if (min.error) {
        spin.fail()
        console.error('\nError minifying: ' + min.error + '\n')
      } else {
        fs.writeFile(
          f.replace('.js', '.min.js'),
          min.code,
          err => {
            if (err) {
              spin.fail()
              console.error('\n' + err + '\n')
            } else {
              spin.succeed()
            }
          }
        )
      }
    }
  })
})
