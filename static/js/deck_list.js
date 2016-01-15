var apiDecksPath = "api/decks";

$(document).ready(function () {
    setupPost();
    fetchJson(createDeckList);
    bindModalButton();
});

function fetchJson(callback) {
    $.get(apiDecksPath, function (data) {
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
            '<tr deck-name="' + deck["name"] + '" class="deck-row">' +
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
                '<td class="text-right">' +
                    '<button class="button-go-deck btn btn-primary">Go to deck</button>' +
                    '<button class="button-delete btn">Delete</button>' +
                '</td>' +
            '</tr>'
        );
    });

    bindButtons();
    bindEditable();
}

function bindButtons() {
    $('.button-go-deck').click(function () {
        document.location = "decks/" + $(this).parent().parent().attr('deck-name');
    });

    $('.button-delete').click(function () {

        var deckName = $(this).parent().parent().attr('deck-name');
        var deleteOk = confirm("Do you really want to delete deck '" + deckName + " ?");

        if (deleteOk) {
            $.ajax({
                url: apiDecksPath + '/' + deckName,
                type: 'delete',
                success: location.reload
            });
        }
    });
}

function bindEditable() {
    $.fn.editable.defaults.mode = 'popup';

    $('.deck-user-index > a').editable({
        type: 'text',
        title: 'Enter new number',
        placement: 'right',

        url: apiDecksPath,
        name: "user_index"
    });

    $('.deck-name > a').editable({
        type: 'text',
        title: 'Enter new name',
        placement: 'right',

        url: apiDecksPath,
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
            $.post(apiDecksPath, postData, function (data) {
                // TODO page should not be refreshed
                //$('#modal-create-deck').modal('hide');
                //$('#modal-form').removeClass('has-error');
                location.reload();
            });
        }
    });
}