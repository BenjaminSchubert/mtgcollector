var iconPath = "/api/icons/";

function insertImagesInText(text) {
    for (var i = 0; i < text.length; ++i) {
        if (text.charAt(i) === '{') {
            var indexClose = text.indexOf('}', i+1); // index of }

            if (indexClose != -1 && indexClose != i+1) {
                text =
                    text.substr(0, i) + // before {
                    '<img src="' + iconPath + text.substr(i+1, indexClose-i-1) + '.png">' + // between {}, transformed
                    text.substr(indexClose + 1); // after }
            }
        }
    }
    return text;
}