$('.csp-setting-sliders input').change(sliderChanged);

function sliderChanged(e) {
	var pref = e.target.name;
	var newWeight = e.target.value;
	
	console.log(pref);
	console.log(newWeight);
	
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
	var maxSize = 15;
	
	for(var i = 0; i < preferences.length; i++)
	{
		console.log(preferences[i]);
		var pref = preferences[i].preference;
		var relWeight = preferences[i].rel_weight;
		var weight = preferences[i].weight;
		
		var relSize = maxSize * relWeight;
		
		$('.csp-settings-relview .csp-' + pref).css({"width" : relSize + "vw", "height" : relSize + "vw"});
		
	}
	
}
