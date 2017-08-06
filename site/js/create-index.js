var lunr = require('lunr')
var fs = require('fs');
var data;

var fs = require('fs');
fs.readFile('build/site/search_data.json', 'utf8', function(err, data) {
    if (err) throw err;
    documents = JSON.parse(data);

    var idx = lunr(function() {
        this.ref('href')
        this.field('title')
        this.field('url')

        for (doc in documents) {
            this.add(documents[doc])
        }
    })

    fs.writeFile('build/site/search_index.json', JSON.stringify(idx), (err) => {
        if (err) throw err;
        console.log('New index file created.');
    });

});
