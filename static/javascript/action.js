



var musicApp = angular.module('musicApp', []). config(['$interpolateProvider',
	function($interpolateProvider) {
		$interpolateProvider.startSymbol('[[');
    	$interpolateProvider.endSymbol(']]');
	}
]);


musicApp.controller('userCtrl', function($scope, $http){

	$scope.userURL = '/login';
	$scope.newUserSelected = false;


	$scope.updateURL = function(url){
		$scope.userURL = url;
	}

	$scope.userFunctions = function(newUserSelected){
		var params = {
			'un': $('#usernameIn').val(),
			'pw': $('#passwordIn').val()
		};

		// alert(newUserSelected);
		var request_url;
		if(newUserSelected){
			request_url = '/handleNewUser';
		}else{
			request_url = '/login';
		}

		$http({
			url: request_url,
			data:params,
			method: 'POST'
		}).then(function success(data){
			console.log('');
			window.location = data.data['url'];
		}, function failure(){
			alert('new user creation failed.');
		});
	}
	
	// $scope.createUser = function(params){
		
	// 	$http({
	// 		url: '/handleNewUser',
	// 		data:params,
	// 		method: 'POST'
	// 	}).then(function success(data){
	// 		console.log('success');
	// 	}, function failure(){
	// 		alert('new user creation failed.');
	// 	});
	// }

	// $scope.loginUser = function(params){

	// 	$http({
	// 		url: '/login',
	// 		method: 'POST',
	// 		data: params
	// 	}).then(function success(data){
	// 		alert(data.data['url']);
	// 		window.location = data.data['url'];
	// 		console.log('');
	// 	});
	// }
});


musicApp.controller('trackDownloadCtrl', function($scope, $http){

    $scope.downloadAvailable = false;
    $scope.downloadMessage = '';
    $scope.currentTrack = {
    	'downloadAvailable': false,
    	'trackName': undefined,
    	'artistName': undefined,
    	'filename': ''
    } 

	$scope.playlistTracks = [];
	$scope.playlistURL = '';
	$scope.curPlaylistTrackURL = '';
	$scope.curPlaylistTrackArtist = '';
	$scope.curPlaylistTrack = '';


	$scope.generatePlaylist = function(name, message){
		//var playlist =  angular.toJson($scope.playlistTracks);
		var playlist = {};
		playlist['tracks'] = $scope.playlistTracks;
		playlist['name'] = name;
		if(message==undefined){message='';}
		playlist['message'] = message;
		playlist['user'] = $('#user').val();
		

		// var stream_url = '/streamPlaylistDownload?parameters=' + encodeURIComponent(JSON.stringify(playlist)); 
		// var source = new EventSource(stream_url);
		// var chunk_size = parseInt(100/playlist['tracks'].length);
		// var progress_width = 0;
  //       source.addEventListener('message', function callback(event){
  //       	alert(event.data);
  //       	if(progress_width<100){
  //       		progress_width = parseInt($('.progress-bar').width()) + chunk_size;
  //       		$('.progress-bar').css('width', progress_width + '%').attr('aria-valuenow', progress_width);
  //       	}else{
  //       		$scope.playlistURL = event.data;
  //       	}
  //       });

  //       return;
  		$('#playlistSuccessModal').modal('show');

		$.ajax({
	        type: 'POST',
	        url: '/downloadPlaylist',
	        dataType:'json',
	        contentType: "application/json",
	        data:  JSON.stringify(playlist),
	        success: function(data) {
	        	console.log(data['playlistURL']);

	        	$scope.$apply(function(){
	        		$scope.playlistURL = data['playlistURL'];
	        	});
	        },
	        error: function(jqXHR, exception) {
	            if (jqXHR.status === 0) {
	                alert('Not connect.\n Verify Network.');
	            } else if (jqXHR.status == 404) {
	                alert('Requested page not found. [404]');
	            } else if (jqXHR.status == 500) {
	                alert('Internal Server Error [500].');
	            } else if (exception === 'parsererror') {
	                alert('Requested JSON parse failed.');
	            } else if (exception === 'timeout') {
	                alert('Time out error.');
	            } else if (exception === 'abort') {
	                alert('Ajax request aborted.');
	            } else {
	                alert('Uncaught Error.\n' + jqXHR.responseText);
	            }
		    }
    	});
	}

	$scope.addTrackToPlaylist = function(curPlaylistTrackURL, curPlaylistTrackArtist, curPlaylistTrack){

		if(curPlaylistTrackURL.indexOf('youtube') > -1 || curPlaylistTrackURL.indexOf('soundcloud') > -1){
			var song = {
				'url': curPlaylistTrackURL,
				'artist': curPlaylistTrackArtist,
				'track': curPlaylistTrack
			}

			$scope.curPlaylistTrackURL = '';
			$scope.curPlaylistTrackArtist = '';
			$scope.curPlaylistTrack = '';

			// push into playlist
			$scope.playlistTracks.push(song);
		}else{
			alert('Must use valid youtube or soundcloud link!');
		}

	}

	$scope.swapMusicSection = function($event, sectionID){
		var currElement =  $(angular.element($event.currentTarget));

		// handle section
		$('.m-section').hide();
		$(sectionID).show();

		// handle menu tab
		$('.m-tab').removeClass('active');
		$(currElement).addClass('active');


		if($event.target.id == 'playlistSectionA'){
			$('#playlistInfoModal').modal('show');
		}else{
			$('#playlistInfoModal').modal('hide');
		}
	}

    $scope.getTrackUrl = function(){
    	var url = '/getTrack?artist=' + $scope.currentTrack.artistName  + '&track_name=' + $scope.currentTrack.trackName + '&track_id=' + $scope.currentTrack.track_id;
    	return encodeURI(url);
    }

	$scope.getTrack = function(youtubeURL, trackName, artistName){

		if(youtubeURL.indexOf('youtube') > -1 || youtubeURL.indexOf('soundcloud') > -1){

			$scope.downloadMessage = 'Please wait for download icon to appear!';
			$('#downloadTrackButton').addClass('disabled');

			var data = $.param({
				youtubeURL: "youtubeURL",
				trackName: "trackName",
				artistName: "artistName"
			});

			var params = {};
			params['youtubeURL'] = youtubeURL;
			params['trackName'] = trackName;
			params['artistName'] = artistName;

			$http({
				method: 'POST',
				url: '/downloadSingleTrack',
				params: params
				// paramSerializer: '$httpParamSerializerJQLike'
			}).then(function success(data){
			    $scope.currentTrack.downloadAvailable = true;
			    $scope.currentTrack.trackName = data.data['track_name'];
			    $scope.currentTrack.artistName = data.data['artist'];
			    $scope.currentTrack.track_id = data.data['track_id'];

			    $scope.trackName = '';
			    $scope.artistName = '';
			    $scope.youtubeURL = '';

			    $scope.downloadMessage = data.data['track_name'] + ' by ' + data.data['artist'];
				$('#downloadTrackButton').removeClass('disabled');
			 
			    console.log('download successful');
			}, function failure(){

			});
		}else{
			alert('Must use valid youtube or soundcloud link!');
		}
	};

	$scope.deleteTrack = function($event, track_id){
			var params = {};
			params['track_id'] = track_id;

			var currElement =  $(angular.element($event.currentTarget));
			currElement.removeClass('glyphicon');
			currElement.removeClass('glyphicon-download-alt');


			$http({
				method: 'POST',
				url: '/deleteTrack',
				params: params
				// paramSerializer: '$httpParamSerializerJQLike'
			}).then(function success(data){			 
			    console.log('track deleted');
				location.reload(); 			    
			}, function failure(){

			});
	};
});




function printJSON(json){
    alert(JSON.stringify(json, null, 2));
    console.log(JSON.stringify(json, null, 2));
}
