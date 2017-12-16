$('.csp-setting-sliders input').change(sliderChanged);

function sliderChanged(e) {
	var pref = e.target.name;
	var newWeight = e.target.value;
	
	//console.log(pref);
	//console.log(newWeight);
	
	$.post(
	    "/user_preference/set/",
	    {
	        "user_preference": pref,
	        "weight": newWeight
	    },
	    function(data) {
			if(data.status == 'success')
			{
				updateUiWeights(data.user_preferences);
			}
	    },
	    "json"
	);	
		
}

function updateUiWeights(preferences) {
	var totalSize = 75;
	var combinedRelWeight = 0;
	
	for(var i = 0; i < preferences.length; i++)
	{
		combinedRelWeight += preferences[i].rel_weight;
	}
	
	var maxSize = totalSize / combinedRelWeight;
	
	for(var i = 0; i < preferences.length; i++)
	{
		console.log(preferences[i]);
		var pref = preferences[i].preference;
		var relWeight = preferences[i].rel_weight;
		var weight = preferences[i].weight;
		console.log(weight);
		
		var relSize = maxSize * relWeight;
		
		$('.csp-settings-relview .csp-' + pref).css({"width" : relSize + "vw", "height" : relSize + "vw"});
		$('.csp-setting-sliders .csp-' + pref +'-value').text(weight + "%");
	}
	
}
