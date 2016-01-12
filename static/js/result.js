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

// current displayed card infos
var curIdDisplayed;



// Allows a callback to be called only when the scroll stops (better performances than just
// calling the callback at each scroll, for example).
// Scroll stop detection is based on a timer of 150ms long.
$.fn.scrollStopped = function(callback) {
    $(this).scroll(function (ev) {
        clearTimeout($(this).data('scrollTimeout'));
        $(this).data('scrollTimeout', setTimeout(callback.bind(this), 150, ev));
    });
};

// Executed at loading
$(document).ready(function () {
    $(window).scrollStopped(loadImagesInViewport); // sets the action to take when scrolling stops
    $(window).resize(initView);

    initView();

    // what to do when clicking on card image
    $('#cards > div').click(lockCardDetails);

    // what to do when hovering on card image
    $('#cards img').hover(function () {
        if (!lockInfo.locked) {
            displayCardDetails($(this).parent().parent().attr('id'));
        }
    });

    // bind update numbers of cards in collection events
    bindUpdateNCardInCollection();
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
    $('#cards > div').height(findImageHeight());
}


function findImageHeight() {
    return $('#cards > div').first().width() * 310 / 223; // 310 : card height, 223 : card width
}

// Unloads each div of #cards not in viewport.
// For those which are :
// sets default image to tag 'img' and loads image based on the 'div' id.
// Once the image is loaded, sets the 'src' attribute to the image path.
function loadImagesInViewport() {

    $('#cards > div').withinviewport().each(function () {
        var curDiv = $(this);
        var curId = curDiv.attr('id');
        var curImg = curDiv.find('img');

        if (!curDiv.hasClass('loaded')) {

            curDiv.addClass('loaded');
            loadedIds.push(curDiv.attr('id'));

            curImg.attr('src', defaultImgPath);
            createStrip(curDiv);

            // Requests loading of the image
            $.ajax(imgPath + curId)

                // image loaded
                .done(function () {
                    curImg.attr('src', imgPath + curId);
                })

                // image failed to load
                .fail(function () {
                    console.log("failed to load image number " + curId);
                });
        }

    });

    unloadNotInViewPort();
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

function createStrip(curDiv) {

    var nNormal = parseInt(curDiv.attr('data-normal'));
    var nFoil = parseInt(curDiv.attr('data-foil'));
    var tot = nNormal + nFoil;
    var innerDiv = curDiv.children('.card-inner');

    if (tot !== undefined && tot > 0) {
        console.log('appending');
        innerDiv.append(
            '<div class="strip"></div>' +
            '<div class="strip-values">' + tot + '</div>'
        );
    }
}

// Locks the details displayed on the card clicked (so hovering on images does not display details of other cards).
// If a card was already locked and the one clicked at this moment is the same, unlock it, else lock the current one.
function lockCardDetails() {

    var curId = $(this).attr('id');

    // lock if no card is clicked
    if (!lockInfo.locked) {
        lockInfo.locked = true;
        lockInfo.lastId = curId;
    } else {

        // unlock if click on same card, otherwise display the current card details
        if (lockInfo.lastId === curId) {
            lockInfo.locked = false;
        } else {
            lockInfo.lastId = curId;
            displayCardDetails(curId);
        }
    }
}

// Opens the details panel of the card clicked.
function displayCardDetails(id) {
    $('#card-details-img').attr('src', imgPath + id);
    fetchCardDetails(id);
}

// If the details for the card whose id is 'id' are not yet fetched, fetches them.
function fetchCardDetails(id) {

    if (detailsFetched[id] === undefined) {

        // loading
        var cardDetails = $('#card-details');
        cardDetails.children('h2').text("Loading...");
        cardDetails.children('#card-details-fields').text("Loading...");
        cardDetails.children('#number-cards-collection').hide();
        curIdDisplayed = id;

        // fetch details
        $.get(detailsPath + id, function (data) {
            detailsFetched[id] = data;
            createDetails(detailsFetched[id]);
        });
    } else {
        createDetails(detailsFetched[id]);
    }
}

function createDetails(details) {

    var cardDetails = $('#card-details');
    cardDetails.children('h2').text(details["name"]);
    cardDetails.children('#card-details-fields').empty();

    if (details["types"][0] !== "Land") {
        createDetailsField(details, "manaCost", "Mana Cost", createStringFromValue);
        createDetailsField(details, "cmc", "Converted Mana Cost", createStringFromValue);
    }
    createDetailsField(details, "types", "Types", createStringFromArrayValue);
    createDetailsField(details, "orig_text", "Card Text", createStringFromValue);
    createDetailsField(details, "flavor", "Flavor Text", createStringFromValue);
    createDetailsField(details, "edition", "Edition", createStringFromValue);
    createDetailsField(details, "rarity", "Rarity", createStringFromValue);
    createDetailsField(details, "number", "Card Number", createStringFromValue);
    createDetailsField(details, "artist", "Artist", createStringFromValue);

    // display inputs
    cardDetails.children('#number-cards-collection').show();
}

// Create a string from a value (in json).
// The resulting string has the \n replaced by <br>. And the placeholder like {W} are replaced with the links to icons.
function createStringFromValue(details, key) {
    return insertImagesInText(("" + details[key]));
}

// Create a string from a value (in json) which is an array. The resulting string has the \n replaced by <br>.
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

function createDetailsField(details, key, name, createStringFunction) {
    // if value at 'key' is set and a key 'key' exists, create the elements
    if (details[key] !== null && details[key] !== undefined) {

        var newDetail = $('<div class="row"></div>');
        newDetail.append('<label class="col-md-4">' + name + '</label>');
        newDetail.append('<div class="col-md-8">' + createStringFunction(details, key).replace(/\n/g, '<br>') + '</div>');

        $('#card-details-fields').append(newDetail);
    }
}

function bindUpdateNCardInCollection() {
    $("#number-cards-collection > div > input").on("change", function() {
        addToCollection(curIdDisplayed, $('#n-normal').val(), $('#n-foil').val(), $('#n-promo').val())
    });
}

function addToCollection(cardId, nNormal, nFoil, nPromo) {

    // setup POST
    var csrftoken = $('meta[name=csrf-token]').attr('content');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    });

    var postData = {
        normal : nNormal,
        foil : nFoil
    };
    console.log(postData);

    $.post("/api/collection/" + cardId, postData , function(data) {
        console.log(data);
    });
}