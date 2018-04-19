$(document).ready(function() {

  function displaySearchResults(results, query, category) {
    $('#results').empty().hide();
    if (results.length) { // Are there any results?
      var appendString = '<table class="table table-striped"><tbody>'

      $.getJSON("/"+searchType+"_search_data.json", function(documents){
        for (r in results) {  // Iterate over the results
          let item = documents[results[r].ref];
          appendString += '<tr><td><p class="lead mb-1"><a href="'+item.url+'" onclick="ga(\'send\', \'event\', \''+category+'\', \'view\', \''+item.title+'\');">'+item.title+'</a> <small>'+item.avnumber+'</small></p><p class="text-muted mb-0">'+item.collection+'</p></td></tr>';
        }
        appendString += '</tbody></table>'
        $('#results').append(appendString);
      });
    }
    $('#results').prepend('<p><span class="badge badge-secondary">'+results.length+'</span> result(s) for <span class="badge badge-secondary">'+query+'</span></p>').fadeIn(200);
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
    $('#results').empty().append('<img class="mx-auto d-block" src="/img/loading.gif" />')
    $('#query').attr("value", searchTerm);

    ga('send', 'event', searchType, 'search', searchTerm);

    $.getJSON("/"+searchType+"_search_index.json", function(data){
      let index = lunr.Index.load(data)

      let results = index.search(searchTerm); // Get lunr to perform a search
      displaySearchResults(results, searchTerm, searchType);

    });

  }

});
