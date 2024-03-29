/**
 * This file contains functions to create view for the cards (loading into viewport, fetching card details, etc).
 * The only thing which is needed when using this file is to define some functions to create the upper and lower
 * parts of the card details and set them at the beginning with the setCreateDetailsFunctions function.
 */

// paths
var imgPath = "/api/images/";
var detailsPath = "/api/cards/";
var defaultImgPath = imgPath + "default.png";

// contains ids of elements which are currently in view port
var loadedIds = [];

// Contains info relative to image locked when image clicked.
// 'locked' is if there is a locked image and 'lastId' is the id of the last card locked.
var lockInfo = {
    locked: false,
    lastId: null
};

// Contains as keys the ids of the cards whose details are already fetched and as values the details as json.
var detailsFetched = {};

// functions to create details on the upper and lower parts of cards details.
// Must be set with a call to setCreateDetailsFunctions before calling createCardDetails.
var createDetailsUpperFunction, createDetailsLowerFunction;

// Allows a callback to be called only when the scroll stops (better performances than just
// calling the callback at each scroll, for example).
// Scroll stop detection is based on a timer of 150ms long.
$.fn.scrollStopped = function(callback) {
    $(this).scroll(function (ev) {
        clearTimeout($(this).data('scrollTimeout'));
        //noinspection JSCheckFunctionSignatures
        $(this).data('scrollTimeout', setTimeout(callback.bind(this), 150, ev));
    });
};

// Executed at loading
$(document).ready(function () {

    // if no result found
    //noinspection JSJQueryEfficiency
    if ($('.card-container').children().length == 0) {
        $('.card-container').append('<p id="no-result-text">No result found</p>');
    }

    else {

        $(window).scrollStopped(loadImagesInViewport); // sets the action to take when scrolling stops
        $(window).resize(initView);

        setImagesErrorPath();
        initView();

        // what to do when clicking on card image
        $('.card').click(lockCardDetails);

        // what to do when hovering on card image
        $('.card img').hover(function () {
            if (!lockInfo.locked) {
                var id = $(this).parent().parent().attr('id');
                // in case of tabs (card id is main-6680 instead of 6880 for ex)
                if (id.indexOf('-') != -1) {
                    id = id.split('-')[1];
                }
                displayCardDetails(id);
            }
        });
    }
});

// Applies the following behaviour on all cards: if image cannot load, displays default image.
function setImagesErrorPath() {
    $('img').attr('onerror', 'this.src="' + defaultImgPath + '"');
}


// Resize divs heights at the right size and loads images
function initView() {
    resizeDivHeights();
    setPreloadMargin($(window).height());
    loadImagesInViewport();
    setPreloadMargin(3 * $(window).height());
}


// Allows loading of cards in a margin of nPixels before the top and after the bottom of viewport.
function setPreloadMargin(nPixels) {
    withinviewport.defaults.top = -nPixels;
    withinviewport.defaults.bottom = -nPixels;
}


// Resize all div to image size.
function resizeDivHeights() {
    $('.card').height(findImageHeight());
}

// Finds the current height of a card.
function findImageHeight() {
    return $('.card').first().width() * 310 / 223; // 310 : card height, 223 : card width
}

// Unloads each div of #cards not in viewport.
// For those which are :
// sets default image to tag 'img' and loads image based on the 'div' id.
// Once the image is loaded, sets the 'src' attribute to the image path.
function loadImagesInViewport() {

    $('.card').withinviewport().each(function () {
        loadImage($(this).attr('id'));
    });

    unloadNotInViewPort();
}

// Loads an image by setting its path once it is fetched.
function loadImage(id) {
    var curDiv = $('#' + id);
    var curImg = curDiv.find('img');

    // in case of tabs (card id is main-6680 instead of 6880 for ex)
    if (id.indexOf('-') != -1) {
        id = id.split('-')[1];
    }

    if (!curDiv.hasClass('loaded')) {

        curDiv.addClass('loaded');
        loadedIds.push(curDiv.attr('id'));

        curImg.attr('src', defaultImgPath);

        var nNormal = parseInt(curDiv.attr('data-normal'));
        var nFoil = parseInt(curDiv.attr('data-foil'));
        createStrip(curDiv, nNormal + nFoil);

        // Requests loading of the image
        $.ajax(imgPath + id)

            // image loaded
            .done(function () {
                curImg.attr('src', imgPath + id);
            })

            // image failed to load
            .fail(function () {
                console.log("failed to load image number " + id);
            });
    }
}

// "Unloads" the cards which are not in view port anymore by changing the 'src' attr of the img tag to "".
function unloadNotInViewPort() {

    for (var i = loadedIds.length-1; i >= 0; i--) {
        var id = loadedIds[i];
        var curDiv = $('#' + id);

        if (!curDiv.is(':within-viewport')) {
            curDiv.removeClass('loaded');
            curDiv.find('img').attr('src', '');

            loadedIds.splice(i, 1);
        }
    }

}

// Creates a strip on the current card.
// 'curDiv' is the node which is the current div of the card.
// 'n' is the number to display on strip.
function createStrip(curDiv, n) {

    // if tot not a valid number
    if (isNaN(n)) {
        return;
    }

    // if strip already existing, update number or remove it if tot = 0
    if (curDiv.find('.strip').length > 0) {
        if (n == 0) {
            curDiv.find('.strip').remove();
            curDiv.find('.strip-values').remove();
        } else {
            curDiv.find('.strip-values').text(n);
        }
        return;
    }

    // strip not yet existing
    var innerDiv = curDiv.children('.card-inner');
    if (n > 0) {
        innerDiv.append(
            '<div class="strip"></div>' +
            '<div class="strip-values">' + n + '</div>'
        );
    }
}

// Locks the details displayed on the card clicked (so hovering on images does not display details of other cards).
// If a card was already locked and the one clicked at this moment is the same, unlock it, else lock the current one.
function lockCardDetails() {

    var id = $(this).attr('id');

    // in case of tabs (card id is main-6680 instead of 6880 for ex)
    if (id.indexOf('-') != -1) {
        id = id.split('-')[1];
    }

    // lock if no card is clicked
    if (!lockInfo.locked) {
        lockInfo.locked = true;
        lockInfo.lastId = id;
    } else {

        // unlock if click on same card, otherwise display the current card details
        if (lockInfo.lastId === id) {
            lockInfo.locked = false;
        } else {
            lockInfo.lastId = id;
            displayCardDetails(id);
        }
    }
}

// Opens the details panel of the card clicked.
function displayCardDetails(id) {
    $('#card-details-img').attr('src', imgPath + id);
    fetchCardDetails(id);
}

// If the details for the card whose id is 'id' are not yet fetched, fetches them.
// When the details are available, call the callback.
function fetchCardDetails(id) {

    if (detailsFetched[id] === undefined) {

        // loading
        var cardDetails = $('#card-details');
        cardDetails.children('h2').text("Loading...");
        cardDetails.children('#card-details-fields').text("Loading...");

        // fetch details
        $.get(detailsPath + id, function (data) {
            detailsFetched[id] = data;
            createDetails(id);
        });
    } else {
        createDetails(id);
    }
}

// Function to call at the beginning to define how to create the card details.
function setCreateDetailsFunctions(createDetailsUpper, createDetailsLower) {
    createDetailsUpperFunction = createDetailsUpper;
    createDetailsLowerFunction = createDetailsLower;
}

// Creates the details view for the current locked card / hovered card.
// The functions createDetailsUpper and createDetailsLower should be set beforehand with
// the function setCreateDetailsFunctions.
function createDetails(id) {

    var details = detailsFetched[id];
    var cardDetails = $('#card-details');

    cardDetails.children('h2').text(details["name"]);
    cardDetails.find('#card-details-upper-right').empty();
    cardDetails.children('#card-details-lower').empty();

    createDetailsUpperFunction(id);
    createDetailsLowerFunction(id);
}

// Create a string from a value (in json).
function createStringFromValue(details, key) {
    return "" + details[key];
}

// Create a string from a value (in json) which is an array.
function createStringFromArrayValue(details, key) {
    var res = "";
    if (details[key].length > 0) {
        res = details[key][0];
        for (var i = 1; i < details[key].length; ++i) {
            res += ", " + details[key][i];
        }
    }
    return res;
}

/**
 * Creates a field corresponding to a detail value.
 *
 * Params :
 * parentDiv : the div to which attach the created element
 * details : object containing values
 * key : the key to access the value which will be displayed
 * name : value of the label
 * colWidthLabel: col width of label
 * colWidthDiv: col width of the div
 * createStringFunction : function which will create a string from the value. Useful to define behaviour related to the
 * value type (for example arrays).
 */
function createDetailsField(parentDiv, details, key, name, colWidthLabel, colWidthDiv, createStringFunction) {
    // if value at 'key' is set and a key 'key' exists, create the elements
    if (details[key] !== null && details[key] !== undefined && details[key] != 0) {
        var newDetail = $('<div class="row"></div>');
        newDetail.append('<label class="col-md-' + colWidthLabel + '">' + name + '</label>');
        newDetail.append('<div class="col-md-' + colWidthDiv + '">' + formatTextToHTMLContent(createStringFunction(details, key)) + '</div>');

        parentDiv.append(newDetail);
    }
}
