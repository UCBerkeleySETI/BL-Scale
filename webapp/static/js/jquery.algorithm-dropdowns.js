

$("#alg_package").change(function() {

	var $dropdown = $(this);

	data = {
		"energy_detection": "energy_detection.py,energy_detection_fine.py,energy_detection_fine_BAT.py,energy_detection_fine_dry_run.py,energy_detection_mid.py",
		"object_detection": "object_detection.py",
		"DeepSeti": "DeepSeti.py"
	}

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