$('.csp-setting-sliders input').change(sliderChanged);

function sliderChanged(e) {
	var pref = e.target.name;
	var newWeight = e.target.value;
	
	console.log(pref);
	console.log(newWeight);
	
	$.post(
	    "/bla/set/",
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

}
