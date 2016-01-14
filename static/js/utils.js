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