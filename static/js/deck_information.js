var deckName = document.location.href.match(/.+\/(.*)$/)[1]; // current deck name
var modifyNumCardPath = "/api/decks/" + deckName + "/";

// Executed when DOM ready
$(document).ready(function () {
    setupPost();
    setCreateDetailsFunctions(createDetailsUpper, createDetailsLower);
    loadAllImages();
});

function loadAllImages() {
    $('.card').each(function() {
        var curDiv = $(this);

        loadImage(curDiv.attr('id'));
        createStrip(curDiv, curDiv.attr('data-number'));
    })
}

// Creates upper part of the card details
function createDetailsUpper(id) {

    var details = detailsFetched[id];
    var parentDiv = $('#card-details-upper-right');

    createButtonRemoveFromDeck(id, parentDiv);

    if (details["types"][0] !== "Land") {
        createDetailsField(parentDiv, details, "manaCost", "Mana Cost", 6, 6, createStringFromValue);
        createDetailsField(parentDiv, details, "cmc", "Cmc", 6, 6, createStringFromValue);
    }
    createDetailsField(parentDiv, details, "types", "Types", 6, 6, createStringFromArrayValue);
    createDetailsField(parentDiv, details, "rarity", "Rarity", 6, 6, createStringFromValue);

    if (details.versions > 1) {
        parentDiv.append('<a href="/card/' + details["name"] + '">See other versions (' + details.versions + ')</a>');
    }
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

// Creates the button to add the current card to a deck.
function createButtonRemoveFromDeck(id, parentDiv) {

    var button = $('<button class="btn btn-primary" data-card-id="' + id + '">Remove from deck</button>');
    var buttonDiv = $('<div class="popover-wrapper"></div>');
    buttonDiv.append(button);

    button.click(function () {

        // create popover content
        var content = '<p>Do you really want to delete this card from this deck ?</p>';

        // create popover
        var popover = createPopover($(content), function () {
            $.ajax({
                url: modifyNumCardPath + id,
                type: 'delete',
                success: function () {
                    location.reload();
                }
            });
        });

        buttonDiv.append(popover);
    });

    parentDiv.append(buttonDiv);
}
