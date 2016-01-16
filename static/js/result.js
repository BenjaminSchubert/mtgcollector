// paths
var numCardPostPath = "/api/collection/";
var deckGetPath = "/api/decks";
var deckPostPath = "/api/decks/";

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

    // if decks could be fetched (user logged in)
    if (existingDecks !== undefined) {
        parentDiv.append('<p>In collection</p>');
        createRowNumCards(parentDiv, id, "Normal", cardDiv.attr('data-normal'), true);
        createRowNumCards(parentDiv, id, "Foil", cardDiv.attr('data-foil'), false);
        createButtonAddToDeck(id, parentDiv);
    }

    if (details["types"][0] !== "Land") {
        createDetailsField(parentDiv, details, "manaCost", "Mana Cost", 6, 6, createStringFromValue);
        createDetailsField(parentDiv, details, "cmc", "Cmc", 6, 6, createStringFromValue);
    }
    createDetailsField(parentDiv, details, "types", "Types", 6, 6, createStringFromArrayValue);
    createDetailsField(parentDiv, details, "rarity", "Rarity", 6, 6, createStringFromValue);

}

// Creates lower parts of card details
function createDetailsLower(id) {
    var details = detailsFetched[id];
    var parentDiv = $('#card-details-lower');

    createDetailsField(parentDiv, details, "orig_text", "Card Text", 4, 8, createStringFromValue);
    createDetailsField(parentDiv, details, "flavor", "Flavor Text", 4, 8, createStringFromValue);
    createDetailsField(parentDiv, details, "edition", "Edition", 4, 8, createStringFromValue);
    createDetailsField(parentDiv, details, "number", "Card Number", 4, 8, createStringFromValue);
    createDetailsField(parentDiv, details, "artist", "Artist", 4, 8, createStringFromValue);
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
        var value = isNormal ? $('#n-normal').text() : $('#n-foil').text();

        var content = $(
            '<label>Number of cards</label>' +
            '<input id="num-cards-to-add" class="form-control" type="number" min="0" value="' + value + '">'
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
                n_normal: n_normal,
                n_foil: n_foil
            };

            $.post(numCardPostPath + id, postData, function (data) {
                // TODO
                link.text(isNormal ? postData.n_normal : postData.n_foil);

                var cardDiv = $('#' + id);
                cardDiv.attr('data-normal', postData.n_normal);
                cardDiv.attr('data-foil', postData.n_foil);
                createStrip(cardDiv);
            });
        });

        row.append(popover);
    });

    parentDiv.append(row);
}

// Creates the button to add the current card to a deck.
function createButtonAddToDeck(id, parentDiv) {

    var button = $('<button id="button-add-to-deck" class="btn btn-primary" data-card-id="' + id + '">Add to deck</button>');
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
                '<input id="new-number-of-cards" class="form-control" type="number" min="0" value="0">' +
                '<label>Add card to side</label>' +
                '<input id="add-to-side" type="checkbox">';

            // create popover
            var popover = createPopover($(content), function () {
                var deckName = $('.popover-main-container').find('#deck-selection').find(":selected").attr('deck-name');

                var postData = {
                    n_cards: $('#new-number-of-cards').val(),
                    side: $('#add-to-side').is(':checked') ? 1 : 0
                };

                $.post(deckPostPath + deckName + "/" + id, postData, function (data) {
                    console.log(data);
                });
            });

        }

        buttonDiv.append(popover);
    });

    parentDiv.append(buttonDiv);
}