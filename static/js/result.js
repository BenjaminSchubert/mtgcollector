
var imgPath = "/api/images/";
var defaultImgPath = imgPath + "default.png";

var loadedIDs = []; // contains ids of elements which are currently in view port

var preLoadMargin = -1000;
withinviewport.defaults.top = preLoadMargin;
withinviewport.defaults.bottom = preLoadMargin;

// Allows a callback to be called only when the scroll stops (better performances than just
// calling the callback at each scroll, for example).
// Scroll stop detection is based on a timer of 250ms long.
$.fn.scrollStopped = function(callback) {
    $(this).scroll(function (ev) {
        clearTimeout($(this).data('scrollTimeout'));
        $(this).data('scrollTimeout', setTimeout(callback.bind(this), 100, ev));
    });
};


$(document).ready(function () {
    $(window).scrollStopped(loadImagesInViewport); // sets the action to take when scrolling stops
    resizeDivHeights();
    loadImagesInViewport();
});


// Resizes all div to image size
function resizeDivHeights() {
    $('#cards').find('> div').height(findImageHeight());
}


function findImageHeight() {
    return $('#cards').find('> div').first().width() * 310 / 223;
}

// Unloads each div of #cards not in viewport.
// For those which are :
// sets default image to tag 'img' and loads image based on the 'div' id.
// Once the image is loaded, sets the 'src' attribute to the image path.
function loadImagesInViewport() {

    $('#cards').find('> div').withinviewport().each(function () {
        var curDiv = $(this);

        if (!curDiv.hasClass('loaded')) {

            loadedIDs.push(curDiv.attr('id'));
            curDiv.addClass('loaded');

            curDiv.children('img').attr('src', defaultImgPath);

            // Requests loading of the image
            $.ajax(imgPath + curDiv.attr('id'))

                // image loaded
                .done(function () {
                    curDiv.children('img').attr('src', imgPath + curDiv.attr('id'));
                })

                // image failed to load
                .fail(function () {
                    console.log("failed to load image number " + curDiv.attr('id'));
                });
        }

    });

    unloadNotInViewPort();
}

// "Unloads" the cards which are not in view port anymore by changing the 'src' attr of the img tag to "".
function unloadNotInViewPort() {

    for (var i = loadedIDs.length-1; i >= 0; i--) {
        var id = loadedIDs[i];
        var notInVP = !$('#' + id).is(':within-viewport');

        if (notInVP) {
            $('#' + id).removeClass('loaded');
            $('#' + id).children('img').attr('src', '');

            loadedIDs.splice(i, 1);
        }
    }

}
