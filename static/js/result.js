// paths
var numCardPostPath = "/api/collection/";
var deckGetPath = "/api/decks";
var deckPostPath = "/api/decks/";

// Contains as keys the ids of the cards whose details are already fetched and as values the details as json.
var detailsFetched = {};

// existing decks, initialized at start
var existingDecks;

// Executed at loading
$(document).ready(function () {
    setupPost();
    fetchExistingDecks();
    setCreateDetailsFunctions(createDetailsUpper, createDetailsLower);
});

function fetchExistingDecks() {
    $.get(deckGetPath, function (data) {
        existingDecks = data.decks;
    });
}

// Creates upper part of the card details
function createDetailsUpper(id) {

    var details = detailsFetched[id];
    var parentDiv = $('#card-details-upper-right');
    var cardDiv = $('#' + id); // TODO: can be changed when cards as json

    parentDiv.append('<p>In collection</p>');
    createRowNumCards(parentDiv, id, "Normal", cardDiv.attr('data-normal'), true);
    createRowNumCards(parentDiv, id, "Foil", cardDiv.attr('data-foil'), false);
    createButtonAddToDeck(id, parentDiv);

    if (details["types"][0] !== "Land") {
        createDetailsField(parentDiv, details, "manaCost", "Mana Cost", createStringFromValue);
        createDetailsField(parentDiv, details, "cmc", "Cmc", createStringFromValue);
    }
    createDetailsField(parentDiv, details, "types", "Types", createStringFromArrayValue);
    createDetailsField(parentDiv, details, "rarity", "Rarity", createStringFromValue);

}

// Creates lower parts of card details
function createDetailsLower(id) {
    var details = detailsFetched[id];
    var parentDiv = $('#card-details-lower');

    createDetailsField(parentDiv, details, "orig_text", "Card Text", createStringFromValue);
    createDetailsField(parentDiv, details, "flavor", "Flavor Text", createStringFromValue);
    createDetailsField(parentDiv, details, "edition", "Edition", createStringFromValue);
    createDetailsField(parentDiv, details, "number", "Card Number", createStringFromValue);
    createDetailsField(parentDiv, details, "artist", "Artist", createStringFromValue);
}

// Creates and editable input for number of cards of a type (normal or foil for example).
function createRowNumCards(parentDiv, id, labelVal, num, isNormal) {
    var row = $('<div class="row popover-wrapper"></div>');
    var label = $('<label class="col-md-9">' + labelVal  + '</label>');
    var link = $('<a class="col-md-3">' + num + '</a>');

    if (isNormal) {
        link.attr('id', 'n-normal');
    } else {
        link.attr('id', 'n-foil');
    }

    row.append(label);
    row.append(link);

    link.click(function () {
        // create popover content
        var content = $(
            '<label>Number of cards</label>' +
            '<input id="num-cards-to-add" type="number" min="0" class="form-control">'
        );

        // create popover
        var popover = createPopover(content, function () {

            var n_normal, n_foil;

            if (isNormal) {
                n_normal = $('#num-cards-to-add').val();
                n_foil = $('#n-foil').text();
            } else {
                n_normal = $('#n-normal').text();
                n_foil = $('#num-cards-to-add').val()
            }

            var postData = {
                id: id,
                n_normal: n_normal,
                n_foil: n_foil
            };

            $.post(numCardPostPath, postData, function (data) {
                link.text(isNormal ? data.normal : data.foil);

                var cardDiv = $('#' + id);
                cardDiv.attr('data-normal', data.normal);
                cardDiv.attr('data-foil', data.foil);
                createStrip(cardDiv);
            });
        });

        row.append(popover);
    });

    parentDiv.append(row);
}

// Creates the button to add the current card to a deck.
function createButtonAddToDeck(id, parentDiv) {

    var button = $('<button class="btn btn-primary" data-card-id="' + id + '">Add to deck</button>');
    var buttonDiv = $('<div class="popover-wrapper"></div>');
    buttonDiv.append(button);

    button.click(function () {

        // if no decks yet
        if (existingDecks.length == 0) {

            var content = '<p>No deck found. Do you want to create one ?</p>';

            // create popover
            var popover = createPopover($(content), function () {
                document.location = "decks";
            });
        }

        // decks exist
        else {

            // create popover content
            var options = "";
            existingDecks.forEach(function (deck) {
                options += '<option deck-name="' + deck["name"] + '">' + deck["name"] + '</option>';
            });

            var content =
                '<label>Deck</label>' +
                '<select id="deck-selection" class="form-control" data-card-id="' + id +'">' +
                    options +
                '</select>' +
                '<label>Number of cards in deck</label>' +
                '<input id="new-number-of-cards" type="number" min="0" class="form-control">' +
                '<label>Add card to side</label>' +
                '<input id="add-to-side" type="checkbox">';

            // create popover
            var popover = createPopover($(content), function () {
                var deckName = $('.popover-main-container').find('#deck-selection').find(":selected").attr('deck-name');

                var postData = {
                    card_id: id,
                    n_cards: $('#new-number-of-cards').val(),
                    side: $('#add-to-side').is(':checked') ? 1 : 0
                };

                $.post(deckPostPath + deckName, postData, function (data) {
                    console.log(data);
                });
            });

        }

        buttonDiv.append(popover);
    });

    parentDiv.append(buttonDiv);
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
