let playlistForm = document.getElementById('pl-form')
let resultElem = document.getElementById('result')

let flashes = document.querySelectorAll('.flashes li')
let spinner = document.querySelector('.spinner')


playlistForm.addEventListener('submit', getResult)

async function getResult() {
  const response = await fetch('/result')
  const result = await response.json()
  resultElem.innerText = `Playlist duration: ${result}`
}

setTimeout(() => {
    flashes.forEach((item) => {
        item.remove()
    })
}, 5000)

spinner.style.display = 'none'
