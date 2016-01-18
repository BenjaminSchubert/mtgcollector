/**
 * Created by Benjamin Schubert and Basile Vu on 1/12/16.
 */

$(document).ready(function () {
    $(".slider").slider({});

    bindSubmitButton();
    bindReplaceMinOneByStar();

    replaceMinOneByStar();

    replaceIcons();
});


function bindSubmitButton() {
    $('#button_submit').click(function (e) {
        var url = $('#form-search input, #form-search select').filter(filterNotDefaultInput).serialize();

        document.location = "search?" + url;
        e.preventDefault(); // prevent default submit event
    });
}

//noinspection JSUnusedLocalSymbols
function filterNotDefaultInput(index, elem) {
    var jElem = $(elem);
    var value = jElem.val();

    // if slider input
    if (jElem.hasClass('slider')) {
        var values = value.split(',');

        return !(parseInt(jElem.attr('data-slider-min')) === parseInt(values[0]) &&
            parseInt(jElem.attr('data-slider-max')) === parseInt(values[1]));
    }

    console.log(elem, value, value !== "");
    return value !== "";
}

function bindReplaceMinOneByStar() {
    $('#form-search').find('input.slider').change(replaceMinOneByStar);
}

function replaceMinOneByStar() {
    $('.slider .tooltip.tooltip-main .tooltip-inner').each(function () {
        $(this).text($(this).text().replace("-1", "*"));
    })
}

function replaceIcons() {
    $('#colors').find('label').each(function () {
        var text = insertImagesInText($(this).text());
        $(this).empty();
        $(this).append(text)
    })
}
