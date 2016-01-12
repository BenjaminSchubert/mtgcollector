var jsonPath = "api/decks/json";

$(document).ready(function () {
    fetchJson(createDeckList);
});

function fetchJson(callback) {
    var testJson = [
        {id: 42, name: "Test", colors: ["{R}", "{G}", "{B}"], cards: 42, side: 14},
        {id: 1, name: "Test2", colors: ["{R}", "{G}", "{W}"], cards: 40, side: 15}
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
                '<th scope="row">' + (i+1) + '</th>' +
                '<td>' + deck.name + '</td>' +
                '<td>' + insertImagesInText(deck.colors.toString()) + '</td>' +
                '<td>' + deck.cards + '</td>' +
                '<td>' + deck.side + '/15</td>' +
                '<td>' +
                    '<button class="btn btn-primary">Go to deck</button>' +
                '</td>' +
            '</tr>'
        );
    });

    bindRows();
}

function bindRows() {
    $('.deck-row button').click(function () {
        document.location = "decks/" + $(this).parentsUntil('.deck-row').parent().attr('id');
    });
}