$(document).ready(function () {
    $('.ui.dropdown').dropdown();
    $('#get_breffi_values').click(function () {
        $.get('/contacts/parse-web/', {}, function (data) { $('#breffi_values_div').html(data) });
    });
});
