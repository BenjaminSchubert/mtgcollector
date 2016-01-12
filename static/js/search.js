/**
 * Created by Benjamin Schubert and Basile Vu on 1/12/16.
 */

$(".slider").slider({});
bindSubmitButton();

function bindSubmitButton() {
    $('#button_submit').click(function (e) {

        var url = $('#form-search input')
            .filter(function (index, element) {
                return $(element).val() != "";
            })
            .serialize();

        document.location = "search?" + url;
        e.preventDefault(); // prevent default submit event
    });
}
