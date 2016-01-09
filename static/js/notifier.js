/**
 * Created by Benjamin Schubert on 1/6/16.
 */

var source = new EventSource('/updates');
source.onmessage = function (event) {
    if(event.data != "ping") {
        $.notify(event.data, {className: "success", position: "right bottom"});
    }
};