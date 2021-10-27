let playlistForm = document.getElementById('playlist-form')
let playlistInput = document.querySelector('input[name=playlist]')
let resultElem = document.getElementById('result')

let spinner = document.querySelector('.spinner')

spinner.style.display = 'none'


playlistForm.addEventListener('submit', async (e) => {
  e.preventDefault()
  resultElem.innerText = ''
  let playlistValue = playlistInput.value
  let pattern = /PL[\w-]{16,34}|OLAK5uy[\w-]{34}/
  let playlistId = playlistValue.match(pattern)

  if (playlistId) {
    spinner.style.display = 'block'
    let result = await getResult(playlistId[0])
    if (result['duration']) {
      spinner.style.display = 'none'
      resultElem.innerHTML = `<h2>${result['duration']}</h2>`
    } 
  } else {
    spinner.style.display = 'none'
    resultElem.innerText = 'Please add a valid link or id.'
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
