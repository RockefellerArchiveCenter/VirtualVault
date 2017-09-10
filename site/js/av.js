window.onload = function() {

	// asset
	var asset = document.getElementById("asset");
	var downloadButton = document.getElementById("download");

	if(asset) {

		// Asset data
		var assetTitle = document.getElementById('asset-title').innerText.trim() || document.getElementById('asset-title').textContent.trim();
		var assetSource = asset.children[0].getAttribute('src');
		var assetType = assetSource.split('.').pop().toUpperCase();
		// get and assign asset size and file type to HTML elements
		var getAssetSize = $.ajax({
			  type: "HEAD",
			  url: assetSource,
			  success: function(msg){
			    var assetByteSize = getAssetSize.getResponseHeader('Content-Length');
					var assetSize = getReadableFileSizeString(assetByteSize);
					document.getElementById('download-details').innerHTML = assetType + '/' + assetSize;
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

		asset.addEventListener('play', function(){
			ga('send', 'event', assetType, 'play', assetTitle);
		});

		asset.addEventListener('pause', function(){
			ga('send', 'event', assetType, 'pause', assetTitle);
		});

		asset.addEventListener('ended', function(){
			ga('send', 'event', assetType, 'ended', assetTitle);
		});

		downloadButton.addEventListener("mousedown", function() {
			ga('send', 'event', assetType, 'download', assetTitle);
		});

		asset.addEventListener("fullscreenchange", function( event ) {
			ga('send', 'event', assetType, 'full screen', assetTitle);
		});
	}
}
