

$("#alg_package").change(function() {

	var $dropdown = $(this);

	data = {
		"energy_detection": "energy_detection.py,energy_detection_fine.py,energy_detection_fine_BAT.py,energy_detection_fine_dry_run.py,energy_detection_mid.py",
		"object_detection": "object_detection.py",
		"DeepSeti": "DeepSeti.py",
		"turboSETI": "turboSETI"
	}

        console.log("data");
        console.log(data)
		var key = $dropdown.val();
		var vals = [];
							
		switch(key) {
		    console.log("in here")
			case 'energy_detection':
				vals = data.energy_detection.split(",");
				break;
			case 'object_detection':
				vals = data.object_detection.split(",");
				break;
			case 'DeepSeti':
				vals = data.DeepSeti.split(",");
				break;
			case 'turboSETI':
			    vals = data.turboSETI.split(",");
			    break;
		}
		
		var $secondChoice = $("#alg_name");
		$secondChoice.empty();
		$.each(vals, function(index, value) {
			$secondChoice.append("<option>" + value + "</option>");
		});

});