/* global XMLHttpRequest, uniqid */
/* === Toggle to show/hide full OP === */
function displayOp (el) { // eslint-disable-line
  var id = el.getAttribute('data-op-id')
  var ed = document.querySelector('#opedition-' + id)
  var op = document.querySelector('#op-' + id)

  if (op.style.display === 'block') {
    ed.style.display = 'block'
    op.style.display = 'none'
    el.innerHTML = 'Show OP'
  } else {
    ed.style.display = 'none'
    op.style.display = 'block'
    el.innerHTML = 'Hide OP'
  }
}

/* === Check for thread changes === */
function checkChanges () {
  var xhttp = new XMLHttpRequest()

  xhttp.onreadystatechange = function () {
    if (xhttp.readyState === 4 && xhttp.status === 200) {
      if (uniqid !== xhttp.responseText.trim()) document.location.reload()
    }
  }

  xhttp.open('GET', '/threadsid.txt', true)
  xhttp.send()
}

setInterval(checkChanges, 60000)
