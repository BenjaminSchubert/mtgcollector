var jsonPath = "api/decks/json";
var deckPostPath = "api/decks";

$(document).ready(function () {
    setupPost();
    fetchJson(createDeckList);
});

function fetchJson(callback) {
    var testJson = [
        {id: 42, user_index: 1, name: "Test", colors: ["{R}", "{G}", "{B}"], n_cards: 42, side: 14},
        {id: 1, user_index: 3, name: "Test2", colors: ["{R}", "{G}", "{W}"], n_cards: 40, side: 15}
    ]
    callback(testJson);
    //$.get(jsonPath, callback(data));
}

function createDeckList(json) {
    var deckList = $('#deck-list > tbody');

    $.each(json, function (i, deck) {

        console.log(deck);

        deckList.append(
            '<tr id="' + deck.id + '" class="deck-row">' +
                '<th class="deck-user-index" scope="row">' +
                    '<a href="#" value="' + deck.user_index + '" data-pk="' + deck.id + '">' +
                        deck.user_index +
                    '</a>' +
                '</th>' +
                '<td class="deck-name">' +
                    '<a href="#" value="' + deck.name + '" data-pk="' + deck.id + '">' +
                        deck.name +
                    '</a>' +
                '</td>' +
                '<td class="deck-colors">' + insertImagesInText(deck.colors.toString()) + '</td>' +
                '<td class="deck-n_cards">' + deck.n_cards + '</td>' +
                '<td class="deck-side">' + deck.side + '/15</td>' +
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