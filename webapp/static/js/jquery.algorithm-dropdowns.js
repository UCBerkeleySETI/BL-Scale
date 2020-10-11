$("#alg_package").change(function() {

	var $dropdown = $(this);

	$.getJSON("./algorithm_dropdowns.json", function(data) {
    
        console.log("dependant dropdowns")
		var key = $dropdown.val();
		var vals = [];
							
		switch(key) {
			case 'energy_detection':
				vals = data.energy_detection.split(",");
				break;
			case 'object_detection':
				vals = data.object_detection.split(",");
				break;
			case 'DeepSeti':
				vals = data.DeepSeti.split(",");
				break;
		}
		
		var $secondChoice = $("#alg_name");
		$secondChoice.empty();
		$.each(vals, function(index, value) {
			$secondChoice.append("<option>" + value + "</option>");
		});

	});
});