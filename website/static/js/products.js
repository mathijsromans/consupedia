$('.csp-rater').each(initRater);
$('.csp-active-user .csp-user-rating i').click(changeRating);

function initRater() {
	var globalRating = $(this).data('global-rating');
	var userRating = $(this).data('user-rating');
	if (userRating > 0) {
		$(this).addClass('csp-user-rated');
		updateUiUserRating($(this), userRating);
	}
	if (globalRating == "None") globalRating = 0;
	updateUiGlobalRating($(this), globalRating);	
}

function updateUiUserRating(rater, rating) {
	var stars = rater.find('.csp-user-rating i');
	stars.each(function() {
		if($(this).index() < rating) $(this).addClass('csp-starred');
		else $(this).removeClass('csp-starred');
	});
}

function updateUiGlobalRating(rater, rating) {
	var starContainer = rater.find('.csp-global-rating');
	if (!starContainer.data('initialWidth')) starContainer.data('initialWidth', starContainer.width());
	var totalWidth = starContainer.data('initialWidth');
	var desiredWidth = totalWidth / 5 * rating;
	
	starContainer.css('width', desiredWidth + 'px');
	
}

function changeRating(e) {
	var rating = $(e.target).index() + 1;
	var rater = $(e.target).closest('.csp-rater');
	rater.data('user-rating', rating);
	rater.addClass('csp-user-rated');

	updateUiUserRating(rater, rating);

	$.post(
	    "/product/rating/set/",
	    {
	        product_id: rater.data('product-id'),
	        rating: rating
	    },
	    function(data) {
			if(data.status == 'success')
			{
				var avg = data.average_rating;
				rater.data('global-rating', avg);
				updateUiGlobalRating(rater, avg);
			}
	    },
	    "json"
	);
}