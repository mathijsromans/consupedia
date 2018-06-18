$('.food').click(selectIngredient);

function selectIngredient(e) {
	var ingredientId = this.id;
	$.post(
	    "/what_to_eat/get_result/",
	    {
	        'ingredient_id': ingredientId,
	    },
	    function(data) {
            var product = data[0];
            var score = data[1];
            var name = product.fields["name"];
            var thumb_url = product.fields["thumb_url"];
            var price = product.fields["price"];
            var environment = score.fields["environment"] ? score.fields["environment"] : "onbekend" ;
            var social = score.fields["social"] ? score.fields["social"] : "onbekend";
            var animals = score.fields["animals"] ? score.fields["animals"] : "onbekend";
            var personal_health = score.fields["personal_health"] ? score.fields["personal_health"] : "onbekend";
            var htmlResult = "<p>" + name + " is het beste product voor jou</p>"
            htmlResult += thumb_url ? "<img src=\'" + thumb_url + "'></img>": "";
            htmlResult += "<p>scores: Milieu ("+ environment + "), "
            htmlResult += "Mensenrechten ("+ social + "), "
            htmlResult += "Dierenwelzijn ("+ animals + "), "
            htmlResult += "Gezondheid ("+ personal_health + ")</p>"
            $("#resultProduct").html(htmlResult);
	    },
	    "json"
	);
}