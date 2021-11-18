# /sug/.rocks
[![Standard - JavaScript Style Guide](https://img.shields.io/badge/code%20style-standard-green.svg)](http://standardjs.com/)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Gitlab Pipeline Status](https://gitlab.com/ctoon/sug/website/badges/master/pipeline.svg)](https://gitlab.com/ctoon/sug/website/-/commits/master)

> [sug.rocks](https://sug.rocks/)


### Table of contents

- [Prerequisites](#prerequisites)
- [Install](#install)
- [Run](#run)
- [Docs](#docs)
- [What about the leakbot?](#what-about-the-leakbot)
- [Compile `SCSS` to `CSS`](#compile-scss-to-css)
- [Linter notes](#linter-notes)
- [Thanks/Credits](#thankscredits)


## Prerequisites
- [NodeJS (w/ npm)](https://nodejs.org/en/) _(not needed for the leakbot)_
    - [yarn](https://yarnpkg.com/)
- [Python 3.7](https://www.python.org/)
    - You can use [pyenv](https://github.com/pyenv/pyenv-installer)
- A webserver (like [Caddy](https://caddyserver.com/))


## Install
```
git clone --recursive https://gitlab.com/ctoon/sug/website.git && cd website
yarn # JS/CSS deps
pip install -r requirements.txt -U # Python deps
cp config/threads-cache.ini.example config/threads-cache.ini
nano templates/op.txt # Add the OP template text here
```

## Run
The `threads.py` script needs to constently run.
You should probably make sure it can restart if it goes down, open a tmux session and use:
```
while true; do python threads.py; sleep 30; done
```

For the download list and the static pages, run:
```
python dllist.py
python static.py
```

And then you just point your favorite webserver _(nginx, caddy, whatevever)_ to the `public/` folder.

## Docs
To compile the docs, install `aglio`.
```
npm install -g aglio
```

Then run it.
```
aglio -i api/sugrocks.apib -o api/index.html
```


## What about the leakbot?
The leakbot has its own repository ([ctoon/sug/leakbot@gitlab](https://gitlab.com/ctoon/sug/leakbot)) and is a gitsubmodule in this repo.

If you forgot to do the `--recursive` when cloning: `git submodule init && git submodule update`


## Compile `SCSS` to `CSS`
**With the [`sass` tool](http://sass-lang.com/install) in your powerful terminal**
```
sass public/scss/light.scss public/css/light.css --style compressed
sass public/scss/dark.scss public/css/dark.css --style compressed
sass public/scss/tumblr.scss public/css/tumblr.css --style compressed
```

**With the [Koala app](http://koala-app.com/)**
- Add the `public` folder.
- Only set `scss/dark.scss`, `scss/light.scss` and `scss/tumblr.scss` to Auto Compile, remove the other stuff.
- Enable the "Source Map" and "Unix New Lines" options.
- Make sure the "Output Style" is set to compressed.
- Right-click and `Set Output Path` to the right `css/*.css` file for the selected `.scss`.
- Edit your files with the app open in the background or press the compile button every time.

You should get something like this:
![](https://s.kdy.ch/koala_2016-12-12_22-01-16.png)


## Linter notes
Make sure your code uses the [`standard-js`](http://standardjs.com/) and
[`PEP8`](https://www.python.org/dev/peps/pep-0008/) standard styles (with minor exceptions).
```
# Test JS
npm test

# Test Python
flake8 --max-line-length=140 .
```

I'd recommand to install the corresponding linter plugins for your code IDE
(like Atom, Sublime Text, VSCode, ...) to help you.


## Thanks/Credits
- People who donated for more server time
- Dingo for the explanations used in leakbot
- The YayPonies guys for the HD rips
- Anons from /sug/
- Cartoon Network and the Steven Universe team for this awesome show
- [BASC-py4chan](https://github.com/bibanon/BASC-py4chan) by [Bibliotheca Anonoma](https://github.com/bibanon)
- [Font Awesome](http://fontawesome.io) by Dave Gandy
