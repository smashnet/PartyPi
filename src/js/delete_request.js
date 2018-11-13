//postData(`http://example.com/answer`, {answer: 42})
//  .then(data => console.log(JSON.stringify(data))) // JSON-string from `response.json()` call
//  .catch(error => console.error(error));

export function deleteData(url = ``) {
  // Default options are marked with *
    return fetch(url, {
        method: "DELETE", // *GET, POST, PUT, DELETE, etc.
        mode: "cors", // no-cors, cors, *same-origin
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        credentials: "same-origin", // include, *same-origin, omit
        headers: {
            // "Content-Type": "application/json; charset=utf-8",
             "Content-Type": "application/x-www-form-urlencoded",
        },
        redirect: "follow", // manual, *follow, error
        referrer: "no-referrer", // no-referrer, *client
    })
    .then(() => location.reload(true)); // parses response to JSON
}
