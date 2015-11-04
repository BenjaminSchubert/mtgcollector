// Loads image urls when the div containing images appear
$(document).ready(function () {
    $('#cards > div').on('appear', function (e) {
        $.get('images/' + e.attr('id'), function(res) {
            e.children('img').attr('src', res);
        });
    });
});