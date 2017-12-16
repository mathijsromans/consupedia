$('#get-recipes').click(getRecipes);

function getRecipes(e) {
	console.log("test");
	var pref = e.target.name;

	$.post(
	    "/recipes/get_for_user",
	    {},
	    function(data) {
			if(data.status == 'success')
			{
				showRecipes(data.recipes)
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
		var div = '<div class="panel panel-primary recipe-item">' 
		+ '<div class="panel-heading"><h3 class="panel-title">' 
		+ name + '</h3></div><div class="panel-body">'+ content +'</div></div>';

		$("#recipes-list").append(div);
	});
}