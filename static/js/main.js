$(document).ready(function () {
	$('.delete-transaction').click(function () {
		var id = $(this).attr('data-id');
		var url = $(this).attr('data-url');

		$('.modal-form', 'input').val(id);
		$('.modal-form').attr('action', url);
	});
	$('.edit-transaction').click(function () {
		var id = $(this).attr('data-id');
		var date = $(this).attr('data-date');
		var bank = $(this).attr('data-bank');
		var amount = $(this).attr('data-amount');
		var description = $(this).attr('data-description');
		var url = $(this).attr('data-url');
		var category = $(this).attr('data-category');
 		var formattedDateString = date.replace(/\//g, "-");

		$('#date').val(formattedDateString);
		$('#amount').val(amount);
		$('#description').val(description);
		$('#category_selector').val(category);

		// Add the "selected" attribute to the first option
		if (bank == "Revolut") {
			$('#Revolut').attr("selected", "selected");
		} else if(bank == "BuddyBank") {
			$('#BuddyBank').attr("selected", "selected");
		} else if(bank == "Popso") {
			$('#Popso').attr("selected", "selected");
		}else {
			$('#Cash').attr("selected", "selected");

		}


		$('.modal-form', 'input').val(id);

		$('.modal-form').attr('action', url);

	});
	$(".goTop").click(function(){scroll(0,0)});
});

