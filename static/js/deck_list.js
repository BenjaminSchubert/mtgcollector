var jsonPath = "api/decks/json";

$(document).ready(function () {
    fetchJson(createDeckList);
    bindRows();
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
            '<tr id="' + deck.id + '" class="deck-values">' +
                '<th scope="row">' + (i+1) + '</th>' +
                '<td>' + deck.name + '</td>' +
                '<td>' + insertImagesInText(deck.colors.toString()) + '</td>' +
                '<td>' + deck.cards + '</td>' +
                '<td>' + deck.side + '/15</td>' +
            '</tr>'
        );
    });
}

function bindRows() {
    $('.deck-values').click(function () {
        //console.log($(this).attr('id'));
        document.location = "decks/" + $(this).attr('id');
    });
}