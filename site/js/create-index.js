var lunr = require('lunr')
var fs = require('fs');
var data;
var indexTypes = ["catalogued-reports", "moving-image", "audio"]

var fs = require('fs');

for (var t in indexTypes) {
  buildIndex(t);
}

function buildIndex(iterator) {
  fs.readFile('build/site/'+indexTypes[iterator]+'_search_data.json', 'utf8', function(err, data) {
      if (err) throw err;
      documents = JSON.parse(data);

      var idx = lunr(function() {
          this.ref('href')
          this.field('title')
          this.field('avnumber')
          this.field('url')
          this.field('collection')

          for (doc in documents) {
              this.add(documents[doc])
          }
      })

      fs.writeFile('build/site/'+indexTypes[iterator]+'_search_index.json', JSON.stringify(idx), (err) => {
          if (err) throw err;
          console.log('New '+indexTypes[iterator]+' index file created.');
      });

  });

}
