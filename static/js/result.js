
var imgPath = "/api/images/";
var defaultImgPath = imgPath + "default.png";

$(document).ready(function () {
    $(window).scroll(loadImagesInViewport); // sets the action to take when scrolling
    loadImagesInViewport(); // fetches the urls for the images on screen at page loading
});

// For each div of #cards visible on screen:
// sets default image to tag 'img' and  fetches the url of the real image based on the 'div' id.
// Once the url is fetched, sets the'src' attribute to the 'img' tag.
function loadImagesInViewport() {
    $("#cards > div").withinviewport().each(function () {
        $(this).children('img').attr('src', defaultImgPath);
        $.get(imgPath + $(this).attr('id'), function(res) {
            $(this).children('img').attr('src', res);
        });
    });
}