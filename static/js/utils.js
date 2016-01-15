var iconPath = "/api/icons/";

// Placeholders like {W} are replaced with the url to icons (iconPath + W.png in this example).
function insertImagesInText(text) {
    return text.replace(/{([^{}]+)}/g, '<img src="' + iconPath + '\$1.png">');
}

// Formats text to html content. \n become <br> and first values (+1 : ...) are in bold (<b>+1</b> : ...).
function formatTextToHTMLContent(text) {
    // replace \n
    text = text.replace(/\n/g, '<br>');

    // first values in bold
    text = text.replace(/(^|<br>)([\+\-][^:]+:)/g, "\$1<b>\$2</b>");

    return text;
}

function setupPost() {
    // setup POST
    var csrftoken = $('meta[name=csrf-token]').attr('content');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    });
}

function createPopover(node, buttonOkFunc) {

    // close other popovers
    $('.popover-main-container').remove();

    var nodeContainer = $('<div class="popover-node-container"></div>');
    nodeContainer.append(node);

    var buttonOk = $(
        '<button type="submit" class="btn btn-primary">' +
            '<i class="glyphicon glyphicon-ok"></i>' +
        '</button>'
    );

    var buttonCancel = $(
        '<button type="button" class="btn">' +
            '<i class="glyphicon glyphicon-remove"></i>' +
        '</button>'
    );

    buttonOk.click(function () {
        buttonOkFunc();
        $('.popover-main-container').remove();
    });

    buttonCancel.click(function () {
        $('.popover-main-container').remove();
    });

    var buttons = $(
        '<div class="popover-buttons">' +
            '<div class="container-fluid">' +
                '<div class="row"></div>' +
            '</div>' +
        '</div>'
    );

    buttons.find('.row').append(buttonOk, buttonCancel);

    var container = $('<div class="popover-main-container container-fluid"></div>');
    container.append(nodeContainer, buttons);

    // bond enter key to submit button
    $(document).keypress(function(e){
        if (e.which == 13){
            buttonOk.click();
        }
    });

    return container;
}