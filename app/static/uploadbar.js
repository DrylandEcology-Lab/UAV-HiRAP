$(document).ready(function(){
	
	$('form').on('submit', function(event) {
			
		event.preventDefault();
			
		var formData = new FormData($('form')[0]);
			
		$.ajax({
			xhr: function(){
				var xhr = new window.XMLHttpRequest();
				
				xhr.upload.addEventListener('progress', function(e) {
					
					if (e.lengthComputable) {
						
						console.log('Bytes loaded: ' + e.loaded);
						console.log('total Size:' + e.total);
						console.log('Percentage Uploaded: ' + (e.loaded / e.total))
						
						var percent = Math.round((e.loaded / e.total) * 100);
						
						$('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%')
					
					}
				
				});
				
				return xhr;
			},
			type: 'POST',
			url: "{{ url_for('main.developing') }}",
			data: formData,
			processData:false,
			contentType:false,
			success: function() {
				
				setTimeout(function(){
					location.reload("{{ url_for('dtc.inproject', username=current_user.username, project_id=DTC_Project.query.order_by(DTC_Project.id.desc()).first().id+1 ) }}");
				}, 1000);
			//	alert('File, uploaded!');
			},
			error: function() {
				
				location.reload("{{ url_for('dtc.decision_tree_submit', username=current_user.username) }}");
				
			}	
		
		});
		
	});
	
});