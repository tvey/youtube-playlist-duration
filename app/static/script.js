let flashes = document.querySelectorAll('.flashes li')

// flashes.forEach((item) => {
//     item.classList.add('fade-out')
// })

setTimeout(() => {
    flashes.forEach((item) => {
        item.remove()
    })
}, 5000)
