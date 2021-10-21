let playlistForm = document.getElementById('playlist-form')
let playlistInput = document.querySelector('input[name=playlist]')
let resultElem = document.getElementById('result')

let flashes = document.querySelectorAll('.flashes li')
let spinner = document.querySelector('.spinner')

playlistForm.addEventListener('submit', async (e) => {
  e.preventDefault()
  let playlistValue = playlistInput.value
  if (playlistValue) {
    spinner.style.display = 'block'
    let result = await getResult(playlistValue)
    spinner.style.display = 'none'
    console.log(`Playlist duration: ${result['duration']}`)
    resultElem.innerText = result['duration']
  }
})

async function getResult(playlistValue) {
  const response = await fetch('/result', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    body: JSON.stringify({'playlist': playlistValue})
    },
  )
  const result = await response.json()
  return result
}

setTimeout(() => {
    flashes.forEach((item) => {
        item.remove()
    })
}, 5000)

spinner.style.display = 'none'
