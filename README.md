# /sug/.rocks
[![Standard - JavaScript Style Guide](https://img.shields.io/badge/code%20style-standard-green.svg)](http://standardjs.com/)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Gitgud Build Status](https://gitgud.io/sug/website/badges/master/build.svg)](https://gitgud.io/sug/website/commits/master)
[![Travis Build Status](https://travis-ci.org/sugrocks/website.svg?branch=master)](https://travis-ci.org/sugrocks/website)

> [sug.rocks](https://sug.rocks/)


### Table of contents

- [Prerequisites](#prerequisites)
- [Install](#install)
- [Run](#run)
- [What about the leakbot?](#what-about-the-leakbot)
- [Compile `SCSS` to `CSS`](#compile-scss-to-css)
- [Linter notes](#linter-notes)
- [Thanks/Credits](#thankscredits)


## Prerequisites
- [NodeJS (w/ npm)](https://nodejs.org/en/) _(not needed for the leakbot)_
    - [yarn](https://yarnpkg.com/)
- [Python 3.6](https://www.python.org/)
    - [pip](https://pip.pypa.io/en/stable/installing/)
    - [pipenv](https://github.com/kennethreitz/pipenv#-installation)
- A webserver (like [Caddy](https://caddyserver.com/))
- Zlib (apt:`zlib1g-dev`) and libjpeg (apt:`libjpeg62-turbo-dev`) _(only needed for the leakbot)_


## Install
```
git clone --recursive https://gitgud.io/sug/website.git && cd website
yarn # JS/CSS deps
pipenv install --python $(which python3.6) # Python deps
cp config/threads-cache.ini.example config/threads-cache.ini
nano templates/op.txt # Add the OP template text here
```

## Run
The `search.py` must be run periodically to check for new thread.  
You could use a cron to run the `pipenv run python search.py`, or open a tmux session and use:
```
while true; do pipenv run python search.py; sleep 120; done # run this in a tmux or screen
```

For the download list and the static pages, run:
```
pipenv run python dllist.py
pipenv run python static.py
```

And then you just point your favorite webserver _(nginx, caddy, whatevever)_ to the `public/` folder.


## What about the leakbot?
The leakbot has its own repository ([sug/leakbot@gitgud](https://gitgud.io/sug/leakbot)) and is a gitsubmodule in this repo.

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

You should get something like that:  
![](https://s.kdy.ch/koala_2016-12-12_22-01-16.png)


## Linter notes
Make sure your code uses the [`standard-js`](http://standardjs.com/) and
[`PEP8`](https://www.python.org/dev/peps/pep-0008/) standard styles (with minor exceptions).
```
# Test JS
npm test

# Test Python
flake8 --ignore=E122,E126,E127,E128 --max-line-length=140 .
```
_(Yes, I ignore stupid warnings that makes the code look more terrible than it is.)_

I'd recommand to install the corresponding linter plugins for your code IDE
(like Atom, Sublime Text, VSCode, ...) to help you.


## Thanks/Credits
- People who donated for more server time
- Dingo for the explanations used in leakbot
- The YayPonies guys for the HD rips
- Anons from /sug/
- Cartoon Network and the Steven Universe team for this awesome show
- [BASC-py4chan](https://github.com/bibanon/BASC-py4chan) & [py8chan](https://github.com/bibanon/py8chan) by [Bibliotheca Anonoma](https://github.com/bibanon)
- [Font Awesome](http://fontawesome.io) by Dave Gandy
