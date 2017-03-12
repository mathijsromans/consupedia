$('.csp-rater').each(initRater);
$('.csp-user-rating i').click(changeRating);


function initRater() {
	var globalRating = $(this).data('global-rating');
	var userRating = $(this).data('user-rating');
	var globalStars = $(this).find('.csp-global-rating');
	var globalStarsInitialWidth = globalStars.width();
	var globalStarsDesiredWidth = globalStarsInitialWidth / 5 * globalRating;
	
	if (userRating > 0) {
		$(this).addClass('csp-user-rated');
		setRating($(this), userRating);
	}
	
	globalStars.css('width', globalStarsDesiredWidth + 'px');
		
}

function setRating(rater, rating) {
	var stars = rater.find('i');

	stars.each(function() {
		if($(this).index() < rating) $(this).addClass('csp-starred');
		else $(this).removeClass('csp-starred');
	});
}

function changeRating(e) {
	var rating = $(e.target).index() + 1;
	var rater = $(e.target).closest('.csp-rater');

	rater.data('user-rating', rating);
	rater.addClass('csp-user-rated');

	setRating(rater, rating);

	$.post(
	    "/product/rating/set/",
	    {
	        product_id: rater.data('product-id'),
	        rating: rating
	    },
	    function(data) {
	        console.log(data.message);
	    },
	    "json"
	);
}