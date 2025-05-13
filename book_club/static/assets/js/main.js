function open_modal(url) {
	$('#edicion').load(url, function () {
		$(this).modal('show');
	});
}