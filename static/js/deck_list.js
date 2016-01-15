var getDeckPath = "api/decks";
var deckPostPath = "api/decks";

// TODO
var test = {
    "decks": [
        {
            "deck_id": 1,
            "n_deck": 0,
            "n_side": 0,
            "name": "Test deck 2",
            "user_id": 1,
            "user_index": 0
        }
    ]
};

$(document).ready(function () {
    setupPost();
    fetchJson(createDeckList);
    bindModalButton();
});

function fetchJson(callback) {
    $.get(getDeckPath, function (data) {
        callback(data);
    });
}

function createDeckList(data) {
    var deckList = $('#deck-list > tbody');
    var decks = data.decks;

    decks.forEach(function (deck) {

        var colorsHTML = "";
        if (deck["colors"] !== undefined && deck["colors"] !== null) {
            colorsHTML = insertImagesInText(deck["colors"].toString());
        }

        deckList.append(
            '<tr id="' + deck["deck_id"] + '" class="deck-row">' +
                '<th class="deck-user-index" scope="row">' +
                    '<a href="#" value="' + deck["user_index"] + '" data-pk="' + deck["deck-id"] + '">' +
                        deck["user_index"] +
                    '</a>' +
                '</th>' +
                '<td class="deck-name">' +
                    '<a href="#" value="' + deck["name"] + '" data-pk="' + deck["deck-id"] + '">' +
                        deck["name"] +
                    '</a>' +
                '</td>' +
                '<td class="deck-colors">' + colorsHTML + '</td>' +
                '<td class="deck-n-deck">' + deck["n_deck"] + '</td>' +
                '<td class="deck-n-side">' + deck["n_side"] + '/15</td>' +
                '<td class="button-go-deck">' +
                    '<button class="btn btn-primary">Go to deck</button>' +
                '</td>' +
            '</tr>'
        );
    });

    bindButtonGoDeck();
    bindEditable();
}

function bindButtonGoDeck() {
    $('.button-go-deck').click(function () {
        document.location = "decks/" + $(this).parent().attr('id');
    });
}

function bindEditable() {
    $.fn.editable.defaults.mode = 'popup';

    $('.deck-user-index > a').editable({
        type: 'text',
        title: 'Enter new number',
        placement: 'right',

        url: deckPostPath,
        name: "user_index"
    });

    $('.deck-name > a').editable({
        type: 'text',
        title: 'Enter new name',
        placement: 'right',

        url: deckPostPath,
        name: "name"
    });
}

function bindModalButton() {
    $('#modal-submit-button').click(function () {
        var postData = {
            name: $('#deck-name').val()
        };

        if (postData.name === "") {
            $('#modal-form').addClass('has-error');
        } else {
            $.post(deckPostPath, postData, function (data) {
                console.log(data);
                $('#modal-add-to-deck').modal('hide');
                $('#modal-form').removeClass('has-error');
            });
        }
    });
}