var isMenuOpen = false

document.querySelector('.nav-toggle').onclick = function () {
  if (isMenuOpen) {
    document.querySelector('.nav-mobile-menu').style.display = 'none'
    isMenuOpen = !isMenuOpen
  } else {
    document.querySelector('.nav-mobile-menu').style.display = 'block'
    isMenuOpen = !isMenuOpen
  }
}
