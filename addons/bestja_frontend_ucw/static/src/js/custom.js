jQuery(window).ready(function () {
    /* Function which changes size of Main top photo snippet when window is resized */
    var windowResize = $(window).on('resize', function () {
        var height = $(this).height() - $("navbar-static-top").height() - 50;
        if (height > 1920) {
            $('.carousel').height(1080);
        } else {
            $('.carousel').height(height);
        }
    });
    /* End of function resize */

    $(".category_link").hover(function () {
        $('img', this).attr("src", function (index, attr) {
            return attr.replace("off", "on");
        });
    }, function () {
        $('img', this).attr("src", function (index, attr) {
            return attr.replace("on", "off");
        });
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
