$('#get-recipes').click(getRecipes);
$('.loader').hide();

function getRecipes(e) {
	var pref = e.target.name;
	$('.loader').show();

	$.post(
	    "/recipes/get_for_user",
	    {},
	    function(data) {
			if(data.status == 'success')
			{
				showRecipes(data.recipes);
				$('.loader').hide();
			}
	    },
	    "json"
	);			
}

function showRecipes(recipeList) {	
	$("#recipes-list").empty();
	recipeList.forEach(function(recipe){
		var name = recipe.name;
		var content = recipe.content;
		var time = recipe.preparation_time_in_min;
		var persons = recipe.number_persons;
		var recipeId = recipe.id;
		var div = '<div class="panel panel-primary recipe-item" id="'+recipeId+'">' 
		+ '<div class="panel-heading"><h3 class="panel-title">' + name + '</h3></div>'
		+ '<div class="panel-body">'+ content +'</div>' 
		+ '<div class="panel-footer">duur:'+ time +' personen: '+persons+'</div>'
		+ '</div>';

		$("#recipes-list").append(div);
		$("#"+ recipeId).click(function(){
			navigateToRecipe(recipeId);
		});
	});
}

function navigateToRecipe(recipeId) {	
	window.location.href = '/recipe/' + recipeId;
}