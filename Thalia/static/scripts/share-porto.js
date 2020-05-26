new ClipboardJS('.btn');

document.addEventListener('click', function (event) {
    // If the clicked element doesn't have the right selector, bail
    if (!event.target.matches('.share-btn')) return;

    // event.target.matches

    // Don't follow the link
    event.preventDefault();

    // Log the clicked element in the console
    console.log(event.target);
    share_portfolio(event.target.dataset.portfolio)

}, false);

Element.prototype.appendAfter = function (element) {
    element.parentNode.insertBefore(this, element.nextSibling);
}, false;

async function share_portfolio(id) {
    const url = `${window.origin}/share/`
    const options = {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({
            portfolio_id: id
        }),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    }

    const response = await fetch(url, options)

    if (response.ok) { // if HTTP-status is 200-299
        // get the response body (the method explained below)
        const uuid = await response.text()
        create_url(uuid, id)
    } else {
        alert("HTTP-Error: " + response.status);
    }
}
function create_url(uuid, id) {
    const a = document.createElement("a")
    const url = window.location.origin + "/dashboard/" + uuid
    const div = document.getElementById(`public-link-div-${id}`)
    const input = document.getElementById(`public-link-${id}`)
    input.value = url
    div.classList.remove('is-hidden')
    console.log(url)
}