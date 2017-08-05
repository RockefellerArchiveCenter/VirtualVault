function displaySearchResults(results, store, query) {
  let searchResults = document.getElementById('results');
  let searchResultsStatus = document.getElementById('results-status');

  if (results.length) { // Are there any results?
    let appendString = '<table class="table table-striped"><tbody>';

    for (var i = 0; i < results.length; i++) {  // Iterate over the results
      let item = store[results[i].ref];
      appendString += '<tr><td><a href="'+item.url+'">'+item.title+'</a></td></tr>';
    }
    appendString += '</tbody></table>'
    searchResults.innerHTML = appendString;
  }
  searchResultsStatus.innerHTML = '<p>Found '+results.length+' result(s) for "'+query+'"</p>', searchResults.children[0];
}

function getQueryVariable(variable) {
  let query = window.location.search.substring(1);
  let vars = query.split('&');

  for (var i = 0; i < vars.length; i++) {
    let pair = vars[i].split('=');

    if (pair[0] === variable) {
      return decodeURIComponent(pair[1].replace(/\+/g, '%20'));
    }
  }
}

let searchTerm = getQueryVariable('q');

if (searchTerm) {
  document.getElementById('results').innerHTML = '<img class="center-block" src="/img/loading.gif" />'
  document.getElementById('query').setAttribute("value", searchTerm);

  let index = lunr(function () { // Initalize lunr
    this.field('id');
    this.field('title');
    this.field('url');
    this.field('record_type');
  });

  for (key in store) { // Add the data to lunr
    index.add({
      'id': key,
      'title': store[key].title,
      'url': store[key].url,
      'record_type': store[key].record_type
    });

    let results = index.search(searchTerm); // Get lunr to perform a search
    displaySearchResults(results, store, searchTerm); // We'll write this in the next section
  }
}
