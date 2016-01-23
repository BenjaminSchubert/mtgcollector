var iconPath = "/api/icons/";

// Placeholders like {W} are replaced with the url to icons (iconPath + W.png in this example).
function insertImagesInText(text) {
    return text.replace(/{([^{}]+)}/g, '<img src="' + iconPath + '\$1.png">');
}

// Formats text to html content (replace \u2212, \n, ...),
// first values (+1 : ...) are in bold (<b>+1</b> : ...),
// adds a <br> as well when there must be one.
// Finally, replaces the placeholders ({W}, for example) by their img tag.
function formatTextToHTMLContent(text) {
    // replace unicode -
    text = text.replace(/\u2212/g, '-');

    // first values in bold
    text = text.replace(/(^|\n|\.)(([\+\-][^:]+|0):)/g, "\$1<br><b>\$2</b>");
    text = text.replace(/^<br>/, "");

    //replace \n isolated
    text = text.replace(/\n/g, "<br>");

    // adds a <br> where there is .{...}
    text = text.replace(/(\.)({[^{}]+})/g, "$1<br>$2");

    // remove a <br> if there is two following each other
    text = text.replace(/<br>(<br>)/g, "$1");
    
    // replace placeholders
    text = insertImagesInText(text);

    return text;
}

// Prepare token for POST requests.
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

// Creates a popover with the desired content and two buttons : cancel and ok.
// The content of the popover is passed as a node and what the button "ok" is doing is defined by the function buttonOkFunc.
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

// Forbids inputting negative numbers in input which are of type "number".
function noNegInputNum() {
    $('input[type="number"]')
}