window.onload = function() {

	// asset
	var asset = document.getElementById("asset");

	if(asset) {

		// Asset data
		var assetSource = asset.children[0].getAttribute('src');
		// get and assign asset size and file type to HTML elements
		var getAssetSize = $.ajax({
			  type: "HEAD",
			  url: assetSource,
			  success: function(msg){
			    var assetByteSize = getAssetSize.getResponseHeader('Content-Length');
					var assetSize = getReadableFileSizeString(assetByteSize);
					document.getElementById('download-details').innerHTML = '(' + assetSize + ')';
			  }
			});

		// Convert bytes to human readable string
		function getReadableFileSizeString(fileSizeInBytes) {
				var i = -1;
				var byteUnits = [' kB', ' MB', ' GB', ' TB', 'PB', 'EB', 'ZB', 'YB'];
				do {
						fileSizeInBytes = fileSizeInBytes / 1024;
						i++;
				} while (fileSizeInBytes > 1024);
				return Math.max(fileSizeInBytes, 0.1).toFixed(1) + byteUnits[i];
		};

	}
}
