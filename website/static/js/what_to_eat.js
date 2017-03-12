$('.category').click(selectCategory);

function selectCategory(e) {
	var categoryId = this.id;    
	$.post(
	    "/what_to_eat/get_result/",
	    {
	        'category_id': categoryId,            
	    },
	    function(data) {
            var name = data.fields["name"];
            $("#resultProduct").html("<p>" + name + "</p>");
	    },
	    "json"
	);
}