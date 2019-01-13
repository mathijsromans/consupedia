$("#priceNotImportant").click(function(e) { saveUserPreference(e, "price", 10); });
$("#priceMediumImportant").click(function(e) { saveUserPreference(e,"price", 50); });
$("#priceVeryImportant").click(function(e) { saveUserPreference(e,"price", 100); });

function saveUserPreference(event, preference, newWeight) {
	$(event.target).parent().find(".questionnaire-answer_selected").removeClass("questionnaire-answer_selected");
	$(event.target).addClass("questionnaire-answer_selected");
	$.post(
	    "/user_preference/set/",
	    {
	        "user_preference": preference,
	        "weight": newWeight
	    },
	    function(data) {
			if(data.status == 'success')
			{
				console.log("weight changed.")
			}
	    },
	    "json"
	);		
};