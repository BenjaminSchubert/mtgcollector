var jsonPath = "api/decks/json";

$(document).ready(function () {
   fetchJson(createDeckList);
});

function fetchJson(callback) {
    var testJson = [
        {name: "Test", colors: ["{R}", "{G}", "{B}"], cards: 42, side: 14},
        {name: "Test2", colors: ["{R}", "{G}", "{W}"], cards: 40, side: 15}
    ]
    callback(testJson);
    //$.get(jsonPath, callback(data));
}

function createDeckList(json) {

    var deckList = $('#deck-list > tbody');

    $.each(json, function (i, deck) {

        console.log(deck);

        deckList.append(
            '<tr>' +
                '<th scope="row">' + i + '</th>' +
                '<td>' + deck.name + '</td>' +
                '<td>' + insertImagesInText(deck.colors.toString()) + '</td>' +
                '<td>' + deck.cards + '</td>' +
                '<td>' + deck.side + '/15</td>' +
            '</tr>'
        );
    });
}