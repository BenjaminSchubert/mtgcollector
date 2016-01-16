// paths
var decksGetPath = "/api/decks";
var decksPath = "/api/decks/";

// executed when DOM ready
$(document).ready(function () {
    setupPost();
    fetchJson(createDeckList);
    bindModalButton();
});

function fetchJson(callback) {
    $.get(decksGetPath, function (data) {
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

        var deckRow = $(
            '<tr deck-name="' + deck["name"] + '" class="deck-row">' +
                '<th class="deck-user-index" scope="row"></th>' +
                '<td class="deck-name"></td>' +
                '<td class="deck-colors">' + colorsHTML + '</td>' +
                '<td class="deck-n-deck">' + deck["n_deck"] + '</td>' +
                '<td class="deck-n-side">' + deck["n_side"] + '/15</td>' +
                '<td class="text-right">' +
                    '<button class="button-go-deck btn btn-primary">Go to deck</button>' +
                    '<button class="button-delete btn">Delete</button>' +
                '</td>' +
            '</tr>'
        );

        deckList.append(deckRow);

        createName(deckRow.find('.deck-name'), deck["name"]);
        createUserIndex(deckRow.find('.deck-user-index'), deck["user_index"]);
    });

    bindButtons();
}

function createName(parent, origDeckName) {
    var wrapper = $('<div class="popover-wrapper"></div>');
    var editable = $('<a class="editable">' + origDeckName + '</a>');

    editable.click(function () {

        var deckName = wrapper.parent().parent().attr('deck-name');

        var content =
            '<label>Enter new value</label>' +
            '<input id="new-name" type="text" class="form-control" value="' + deckName + '">';

        var popover = createPopover($(content), function () {
            var path = decksPath + deckName + "/rename";
            var newName = $('#new-name').val();

            var postData = {
                name: newName
            };

            $.post(path, postData, function () {
                //success
                editable.text(newName);
                wrapper.parent().parent().attr('deck-name', newName);
            });
        });

        wrapper.append(popover);
    });

    wrapper.append(editable);
    parent.append(wrapper);
}

function createUserIndex(parent, origUserIndex) {
    var wrapper = $('<div class="popover-wrapper"></div>');
    var editable = $('<a class="editable">' + origUserIndex + '</a>');

    editable.click(function () {

        var deckName = wrapper.parent().parent().attr('deck-name');
        var userIndex = wrapper.parent().siblings('.deck-user-index').text();

        var content = $(
            '<label>Enter new value</label>' +
            '<input id="new-user-index" type="number" class="form-control" min="0" value="' + userIndex + '">'
        );

        var popover = createPopover($(content), function () {
            var path = decksPath + deckName + "/index";
            var newIndex = $('#new-user-index').val();

            var postData = {
                index: newIndex
            };

            $.post(path, postData, function () {
                // success
                editable.text(newIndex);
            });
        });

        wrapper.append(popover);
    });

    wrapper.append(editable);
    parent.append(wrapper);
}

function bindButtons() {
    $('.button-go-deck').click(function () {
        document.location = "decks/" + $(this).parent().parent().attr('deck-name');
    });

    $('.button-delete').click(function () {

        var deckName = $(this).parent().parent().attr('deck-name');
        var deleteOk = confirm("Do you really want to delete deck \"" + deckName + "\" ?");

        if (deleteOk) {
            $.ajax({
                url: decksPath + deckName,
                type: 'delete',
                success: function () {
                    location.reload();
                }
            });
        }
    });
}

function bindModalButton() {
    $('#modal-submit-button').click(function () {
        var deckName = $('#deck-name').val();

        if (deckName.name === "") {
            $('#modal-form').addClass('has-error');
        } else {
            $.post(decksPath + deckName, {}, function () {
                // TODO page should not just be refreshed
                //$('#modal-create-deck').modal('hide');
                //$('#modal-form').removeClass('has-error');
                location.reload();
            });
        }
    });
}
