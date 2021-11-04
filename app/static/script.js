let playlistForm = document.getElementById('playlist-form')
let playlistInput = document.getElementById('playlist-input')
let resultElem = document.getElementById('result')
let showMore = document.getElementById('more')
let showMoreBtn = document.querySelector('#more button')
let spinner = document.querySelector('.spinner')

spinner.style.display = 'none'

playlistForm.addEventListener('submit', async (e) => {
  e.preventDefault()
  resultElem.innerText = ''
  showMore.style.display = 'none'
  let playlistValue = playlistInput.value
  let pattern = /PL[\w-]{16,34}|OLAK5uy[\w-]{34}/
  let playlistId = playlistValue.match(pattern)

  if (playlistId) {
    spinner.style.display = 'block'
    let result = await getResult(playlistId[0])
    spinner.style.display = 'none'

    if (result['duration']) {
      let creator = result['channel_title'] ? ` by ${result['channel_title']}` : ''
      let meta = `<strong>${result['playlist_title']}</strong>${creator} (${result['items']})`
      let totalHours = result['total_hours'] ? `(${result['total_hours']}+ hours)` : ''
      resultElem.innerHTML = `
        <p>${meta}</p>
        <h2>${result['duration']} ${totalHours}</h2>
      `
      showMore.style.display = 'block'
      showMoreBtn.addEventListener('click', () => {
        if (showMore.childElementCount == 1) {
          let more = document.createElement('ul')
          more.innerHTML = `
            <li><strong>Avg duration:</strong> ${result['avg_duration']}</li>
            <li><strong>1.25x:</strong> ${result['speed_1.25']}</li>
            <li><strong>1.5x:</strong> ${result['speed_1.5']}</li>
            <li><strong>1.75x:</strong> ${result['speed_1.75']}</li>
            <li><strong>2x:</strong> ${result['speed_2']}</li>
          `
          showMore.appendChild(more)
        } else {
          document.querySelector('#more ul').remove()
        }
      })

    } else if (result['error']) {
      if (result['code'] == 404) {
        resultElem.innerText = "Playlist is private or doesn't exist."
      }
    } else {
      resultElem.innerText = 'Unable to get result for this playlist.'
    }
  } else {
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
