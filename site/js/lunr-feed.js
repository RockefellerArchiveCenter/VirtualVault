function displaySearchResults(results, query) {
  $('#results').empty().hide();
  if (results.length) { // Are there any results?
    let appendString = '<table class="table table-striped"><tbody>';

    $.getJSON("/"+searchType+"_search_data.json", function(documents){
      for (r in results) {  // Iterate over the results
        let item = documents[results[r].ref];
        appendString += '<tr><td><a href="'+item.url+'" onclick="ga(\'send\', \'event\', \'catalogued-reports\', \'view\', \''+item.title+'\');">'+item.title+'</a></td></tr>';
      }
      appendString += '</tbody></table>'
      $('#results').append(appendString);
    });
  }
  $('#results').prepend('<p><span class="badge">'+results.length+'</span> result(s) for <span class="badge">'+query+'</span></p>').fadeIn(200);
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
let searchType = $('form').attr('action').substring(1);

if (searchTerm) {
  $('#results').empty().append('<img class="center-block" src="/img/loading.gif" />')
  $('#query').attr("value", searchTerm);

  ga('send', 'event', 'catalogued-reports', 'search', searchTerm);

  $.getJSON("/"+searchType+"_search_index.json", function(data){
    let index = lunr.Index.load(data)

    let results = index.search(searchTerm); // Get lunr to perform a search
    displaySearchResults(results, searchTerm);

  });

}
