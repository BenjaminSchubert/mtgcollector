// paths
var imgPath = "/api/images/";
var detailsPath = "/api/cards/";
var defaultImgPath = imgPath + "default.png";
var numCardPostPath = "/api/collection/";
var deckPostPath = "api/decks/";

// TODO change once api/decks ok
var existingDecks = [
    {id: 31, name: "Test", user_index: 1, colors:[], n_cards: 42, n_side: 4},
    {id: 22, name: "Deck temp", user_index: 2, colors: [], n_cards: 33, n_side: 10}
];

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

    setImagesErrorPath();
    initView();

    // what to do when clicking on card image
    $('#cards > div').click(lockCardDetails);

    // what to do when hovering on card image
    $('#cards img').hover(function () {
        if (!lockInfo.locked) {
            displayCardDetails($(this).parent().parent().attr('id'));
        }
    });

    bindEditable();
    setupPost();
    prepareDeckModal();
});

function setImagesErrorPath() {
    $('img').attr('onerror', 'this.src="' + defaultImgPath + '"');
}

function prepareDeckModal() {
    var options = '';
    existingDecks.forEach(function (deck) {
        options += '<option deck-id="' + deck.id + '">' + deck.name + '</option>';
    });

    $('#deck-selection').append(options);

    // post data
    $('#modal-submit-button').click(function () {
        var deckId = $('#deck-selection').find(":selected").attr('deck-id');

        var postData = {
            card_id: $('#modal-add-to-deck').attr('card-id'),
            n_cards: $('#number-cards-to-add').val(),
            side : $('#add-to-side').is(':checked')
        };

        $.post(deckPostPath + deckId, postData , function (data) {
            console.log(data);
            $('#modal-add-to-deck').modal('hide');
        });
    });
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


// Resizes all div to image size.
function resizeDivHeights() {
    $('#cards > div').height(findImageHeight());
}

// Finds the current height of a card.
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

// Creates the details view for the current locked card / hovered card
function createDetails(id) {

    var details = detailsFetched[id];
    var cardDetails = $('#card-details');

    cardDetails.children('h2').text(details["name"]);
    cardDetails.find('#card-details-upper-right').empty();
    cardDetails.children('#card-details-lower').empty();
    $('#modal-add-to-deck').attr('card-id', id);

    createDetailsUpper(id);
    createDetailsLower(details);
}

// Creates upper part of the card details
function createDetailsUpper(id) {

    var parentDiv = $('#card-details-upper-right');

    // TODO: can be changed when cards as json
    var cardDiv = $('#' + id);

    parentDiv.append('<p>In collection</p>');
    createRowNumCards(parentDiv, id, "Normal", cardDiv.attr('data-normal'));
    createRowNumCards(parentDiv, id, "Foil", cardDiv.attr('data-foil'));
    createButtonAddToDeck(parentDiv);

    var details = detailsFetched[id];
    if (details["types"][0] !== "Land") {
        createDetailsField(parentDiv, details, "manaCost", "Mana Cost", createStringFromValue);
        createDetailsField(parentDiv, details, "cmc", "Cmc", createStringFromValue);
    }
    createDetailsField(parentDiv, details, "types", "Types", createStringFromArrayValue);
    createDetailsField(parentDiv, details, "rarity", "Rarity", createStringFromValue);

}

// Creates lower parts of card details
function createDetailsLower(details) {
    var parentDiv = $('#card-details-lower');
    createDetailsField(parentDiv, details, "orig_text", "Card Text", createStringFromValue);
    createDetailsField(parentDiv, details, "flavor", "Flavor Text", createStringFromValue);
    createDetailsField(parentDiv, details, "edition", "Edition", createStringFromValue);
    createDetailsField(parentDiv, details, "number", "Card Number", createStringFromValue);
    createDetailsField(parentDiv, details, "artist", "Artist", createStringFromValue);
}

// Creates and editable input for number of cards of a type (normal or foil for example).
function createRowNumCards(parentDiv, id, labelVal, num) {
    var row = $('<div class="row"></div>');
    var label = $('<label class="col-md-9">' + labelVal  + '</label>');
    var input = $('<a>' + num + '</a>').attr({
        'class': 'col-md-3',
        'data-placement': 'left',
        'data-title': 'Number of cards',
        'data-type': 'number',
        'data-url': numCardPostPath + id,
        'data-pk': id,
        'data-name': labelVal
    });

    input.editable();

    row.append(label);
    row.append(input);
    parentDiv.append(row);
}

// Creates the button to add the current card to a deck.
function createButtonAddToDeck(parentDiv) {
    var button = $('<button>Add to deck</button>');

    button.attr({
        'id': 'button-add-to-deck',
        'class': 'btn btn-primary',
        'data-toggle': 'modal',
        'data-target': '#modal-add-to-deck'
    });

    parentDiv.append(button);
}

// Create a string from a value (in json). Placeholders like {W} are replaced with the url to icons.
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

/**
 * Creates a field corresponding to a detail value.
 *
 * Params :
 * parentDiv : the div to which attach the created element
 * details : object containing values
 * key : the key to access the value which will be displayed
 * name : value of the label
 * createStringFunction : function which will create a string from the value. Useful to define behaviour related to the
 * value type (for example arrays).
 */
function createDetailsField(parentDiv, details, key, name, createStringFunction) {
    // if value at 'key' is set and a key 'key' exists, create the elements
    if (details[key] !== null && details[key] !== undefined) {

        var newDetail = $('<div class="row"></div>');
        newDetail.append('<label class="col-md-6">' + name + '</label>');
        newDetail.append('<div class="col-md-6">' + formatTextToHTMLContent(createStringFunction(details, key)) + '</div>');

        parentDiv.append(newDetail);
    }
}

// Binds editable fields.
function bindEditable() {
    var cardDetails = $('#card-details');

    cardDetails.find('#n-normal').editable({
        type: 'number',
        title: 'Enter new number',
        placement: 'left',

        url: numCardPostPath,
        name: "n_normal"
    });

    cardDetails.find('#n-foil').editable({
        type: 'number',
        title: 'Enter new number',
        placement: 'left',

        url: numCardPostPath,
        name: "n_foil"
    });
}