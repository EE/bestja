jQuery(window).ready(function () {

    /* Function which changes size of Main top photo snippet when window is resized */
    var $window = $(window).on('resize', function () {
        var height = $(this).height() - $("navbar-static-top").height() - 50;
        if (height > 1080) {
            $('.main_top_photo_text').height(1080);
        } else {
            $('.main_top_photo_text').height(height);
        }
    });
    /* End of function resize */

    $('.choose_place').click(function () {
        $('html, body').animate({
            scrollTop: $("#choose_place_title").offset().top
        }, 800);
    });

    setInterval(function () {
        $("#down_arrow_scroll").animate({'margin-bottom': '-10px'}, 1000);
        $("#down_arrow_scroll").animate({'margin-bottom': '10px'}, 1000);
    }, 1400);

    /* Smooth scrolling */
    $(function () {
        $('a[href*=#]:not([href=#])').click(function () {
            $('html,body').stop();
            if (location.pathname.replace(/^\//, '') === this.pathname.replace(/^\//, '') && location.hostname === this.hostname) {
                var target = $(this.hash);
                target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                if (target.length) {
                    $('html,body').animate({
                        scrollTop: target.offset().top
                    }, 500);
                    return false;
                }
            }
        });
    });
    /* End of smooth scrolling */
});