// paths
var imgPath = "/api/images/";
var infoPath = "/api/cards/";
var defaultImgPath = imgPath + "default.png";

// contains ids of elements which are currently in view port
var loadedIds = [];

// contains info relative to infos locked when image clicked.
// 'locked' is if there is a locked image and 'lastId' is the id of the last card locked.
var lockInfoCard = {
    locked: false,
    lastId: null
};

// contains as keys the ids of the cards whoses infos are already fetched and as values the infos as json.
var infosFetched = {};



// Allows a callback to be called only when the scroll stops (better performances than just
// calling the callback at each scroll, for example).
// Scroll stop detection is based on a timer of 250ms long.
$.fn.scrollStopped = function(callback) {
    $(this).scroll(function (ev) {
        clearTimeout($(this).data('scrollTimeout'));
        $(this).data('scrollTimeout', setTimeout(callback.bind(this), 100, ev));
    });
};

// Executed at loading
$(document).ready(function () {
    $(window).scrollStopped(loadImagesInViewport); // sets the action to take when scrolling stops
    $(window).resize(initView);

    initView();

    // what to do when clicking on card image
    $('#cards > div').click(lockCardInfos);

    // what to do when hovering on card image
    $('#cards > div > img').hover(function () {
        if (!lockInfoCard.locked) {
            displayCardInfos($(this).parent());
        }
    });
});


// Resize divs heights at the right size and loads images
function initView() {
    resizeDivHeights();
    setPreloadMargin($(window).height());
    loadImagesInViewport();
    setPreloadMargin(3 * $(window).height());
}


// Allows loading of cards in a margin of nPixels before the top and after the bottom of viewport
function setPreloadMargin(nPixels) {
    withinviewport.defaults.top = -nPixels;
    withinviewport.defaults.bottom = -nPixels;
}


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

            loadedIds.push(curDiv.attr('id'));
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

    for (var i = loadedIds.length-1; i >= 0; i--) {
        var id = loadedIds[i];
        var notInVP = !$('#' + id).is(':within-viewport');

        if (notInVP) {
            $('#' + id).removeClass('loaded');
            $('#' + id).children('img').attr('src', '');

            loadedIds.splice(i, 1);
        }
    }

}

// Locks the infos displayed on the card clicked (hovering on images does not display infos of other cards).
// If a card was already locked and the one clicked at this moment is the same, unlock it, else lock the current one.
function lockCardInfos() {

    var currentId = $(this).attr('id');

    // lock if no card is clicked
    if (!lockInfoCard.locked) {
        lockInfoCard.locked = true;
        lockInfoCard.lastId = currentId;
    } else {

        // unlock if click on same card, otherwise display the current card info
        if (lockInfoCard.lastId === currentId) {
            lockInfoCard.locked = false;
        } else {
            lockInfoCard.lastId = currentId;
            displayCardInfos($(this));
        }
    }
}

// Opens the infos panel of the card clicked.
function displayCardInfos(cardDiv) {
    var curId = cardDiv.attr('id');
    var cardInfos = $('#card-infos');

    cardInfos.children('img').attr('src', imgPath + curId);

    var infos = fetchCardInfos(curId);
    cardInfos.children('h2').text(infos["name"]);

    createInfos(infos);
}

// If the infos for the card whose id is 'id' are not yet fetched, fetches them.
function fetchCardInfos(id) {

    if (infosFetched[id] === undefined) {
        // fetch infos
        $.get(infoPath + id, function (data) {
            infosFetched[id] = data;
        });
    }

    return infosFetched[id];
}

function createInfos(infos) {
    $('#card-infos > div').empty();
    createInfoField(infos, "artist");
    createInfoField(infos, "cmc", "Converted Mana Cost");
    createInfoField(infos, "number", "Card Number");
    createInfoField(infos, "artist");
}

function createInfosField(infos, key, name) {
    var parent = $('#card-infos > div');

    parent.append($("<label>" + name.charAt(0).toUpperCase() + name.substr(1, name.length) + "</label>"));
    parent.append($("<div>" + infos[key] + "</div>"));
}

function createInfoField(infos, key) {
    createInfosField(infos, key, key);
}
