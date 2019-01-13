$("#priceNotImportant").click(function(e) { saveUserPreference(e, "price", 1); });
$("#priceMediumImportant").click(function(e) { saveUserPreference(e,"price", 50); });
$("#priceVeryImportant").click(function(e) { saveUserPreference(e,"price", 100); });

$("#noEatMeat").click(function(e) { saveUserPreference(e,"animals", 100, function(){ saveUserPreference(e,"animal_harm", 100);}); });
$("#sometimesEatMeat").click(function(e) { saveUserPreference(e,"animals", 50, function(){ saveUserPreference(e,"animal_harm", 50);}); });
$("#alwaysEatMeat").click(function(e) { saveUserPreference(e,"animals", 1, function(){ saveUserPreference(e,"animal_harm", 1);}); });

function saveUserPreference(event, preference, newWeight, callback) {
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
				if(callback != null && typeof callback === "function")
				{
					callback();
				}
				console.log("weight changed.")
			}
	    },
	    "json"
	);		
};