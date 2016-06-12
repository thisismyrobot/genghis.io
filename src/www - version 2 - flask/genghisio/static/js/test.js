/*

    Baseline reset function

*/
function reset() {

    var android_frame = $('#android_frame');

    // Insert the Android mocks into the Android frame's globals
    android_frame.load(function() {

        var cw = document.getElementById('android_frame').contentWindow;
        cw['Android'] = Android;

        // Ensure the redirects stay in the frame
        cw.genghisio.openUrl = function(url) {
            android_frame.attr('src', url);
        };

        // Grab a copy of the genghisio namespace from the iframe
        android_genghisio = cw.genghisio;

    });
    android_frame.attr('src', '/android');

}

$(document).ready(function() {
    reset();
    $.getScript('/static/js/tests.js');
});
