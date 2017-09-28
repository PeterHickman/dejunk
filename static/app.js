/*globals '$', document */

function tag_multiple_items() {
	var how_many = 0;
	var ids = [];

	$("input[@type=checkbox]:checked").each(function() {
		how_many = how_many + 1;
		ids.push($(this).attr('id').replace('photo_',''));
	});

	if(how_many > 0) {
		$("#ids").val(ids);
		return true;
	}
	else {
		return false;
	}
}

$(document).ready(function () {
    /* Highlight the images by making the background red or green
     * when they are classified.
     */
    $("input[@type=radio]").click(function (index) {
        $(this).parent('center').parent('td').removeClass('ok_b').removeClass('junk_b').removeClass('odd').removeClass('even');
        if ($(this).attr('value') === 'ok') {
            $(this).parent('center').parent('td').addClass('ok_b');
        }
        else {
            $(this).parent('center').parent('td').addClass('junk_b');
        }
    });

    /* If there is some content to classify and javascript is available
     * then we display some links to that will allow the user to set all
     * the unclassified images in one go.
     */

    $("#to_ok").click(function (index) {
        $('td.odd input[@type=radio][@value=ok]').trigger('click');
        $('td.even input[@type=radio][@value=ok]').trigger('click');
    });

    $("#to_junk").click(function (index) {
        $('td.odd input[@type=radio][@value=junk]').trigger('click');
        $('td.even input[@type=radio][@value=junk]').trigger('click');
    });

    $("#to_delete").click(function (index) {
        $('input[@type=checkbox]').trigger('click');
    });
});
