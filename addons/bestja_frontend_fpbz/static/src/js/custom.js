jQuery(window).ready(function () {

    /* Function which changes size of Main top photo snippet when window is resized */
    var $window = $(window).on('resize', function () {
        var height = $(this).height() - $("navbar-static-top").height() - 50;
        $('.main_top_photo_text').height(height);
    });
    /* End of function resize */

        $('.choose_place').click(function () {
        $('html, body').animate({
            scrollTop: $("#map_of_poland_section").offset().top
        }, 800);
    });
});