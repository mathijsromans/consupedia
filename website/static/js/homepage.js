$('#get-recipes').click(getRecipes);
$('.loader').hide();
$("#recipes-list-box").hide();

function getRecipes(e) {
	var pref = e.target.name;
	$('.loader').show();
	console.log(new Date().getTime() + " Start get-recipes")

	$.post(
	    "/recipes/get_for_user",
	    {},
	    function(data) {
			if(data.status == 'success')
			{
				showRecipes(data.recipes);
				$('.loader').hide();
				console.log(new Date().getTime() + " end get-recipes")
			}
	    },
	    "json"
	);			
}

function showRecipes(recipeList) {	
	$("#recipes-list").empty();
	$("#recipes-list-box").show();
	$("#user-preferences-search-recipes").slideUp();
	var resultCount = '<div class="col-sm-12 text-center">' +
		'<h5> Er zijn ' + recipeList.length + ' recepten gevonden op basis van jouw voorkeuren.</h5>' +
		'<button id="show-user-preferences" class="btn btn-primary ml-3">Voorkeuren opnieuw instellen</button>' +
		'<hr class="horizontal-dotted-line">' +
  	'</div>';
	$("#recipes-list").append(resultCount);
	$('#show-user-preferences').click(function(){
		$("#user-preferences-search-recipes").slideDown();
		$('#show-user-preferences').hide();
	});
	recipeList.forEach(function(recipe){
		var name = recipe.name;
		var content = recipe.content;
		var time = recipe.preparation_time_in_min;
		var persons = recipe.number_persons;
		var recipeId = recipe.id;
		var picture_url = recipe.picture_url;
		var pictureBackground = '<img src="'+ picture_url +'" class="recipe-image">';
		var panelFooter = 
		'<div class="panel-footer">' +
			'<div class="row">' +
				'<div class="col-xs-6" align="left">'+
					'<span><i class="fa fa-clock-o"></i> ' +  time+ ' min</span>'+ 
	        	'</div>' +
	        	'<div class="col-xs-6" align="right">'+ 
	        		'<span><i class="fa fa-user"></i> ' + persons + '</span>'
	        	'</div>' +
	        '</div>' +
	    '</div>';

		var div = '<div class="panel panel-primary recipe-item" id="'+recipeId+'">' 
		+ '<div class="panel-heading"><h3 class="panel-title">' + name + '</h3></div>'
		+ '<div class="panel-body">'+ pictureBackground +'</div>' 
		+ panelFooter
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