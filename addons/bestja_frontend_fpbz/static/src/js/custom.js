jQuery(window).ready(function () {

    /* Function which changes size of Main top photo snippet when window is resized */
    var $window = $(window).on('resize', function () {
        var height = $(this).height() - $("navbar-static-top").height() - 50;
        if (height > 1080) {
            $('.introduction').height(1080);
        } else {
            $('.introduction').height(height);
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

    /* Cookie for reminder */
    function setCookie(cookieName, cookieValue, daysToExpire) {
        var d = new Date();
        d.setTime(d.getTime() + (daysToExpire * 24 * 60 * 60 * 1000));
        var expires = "expires=" + d.toUTCString();
        document.cookie = cookieName + "=" + cookieValue + "; " + expires;
    }

    function getCookie(cookieName) {
        var name = cookieName + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ')
                c = c.substring(1);
            if (c.indexOf(name) == 0)
                return c.substring(name.length, c.length);
        }
        return "";
    }

    $('#cookie_reminder_close').click(function(){
        setCookie('cookie_info_dismissed','yes',7);
        $('#cookie_reminder_container').hide();
    });

    if(getCookie('cookie_info_dismissed') === 'yes'){
        $('#cookie_reminder_container').hide();
    }
    /* End of cookie for reminder */

    /* -+- Animations -+- */
    $(window).scroll(function () {

        /* Check the location of each desired element */
        $('.fadeIn').each(function (i) {

            var bottom_of_object = $(this).offset().top + $(this).outerHeight();
            var bottom_of_window = $(window).scrollTop() + $(window).height();

            /* If the object is completely visible in the window, fade it it */
            if (bottom_of_window > bottom_of_object) {

                $(this).animate({
                    'opacity': '1'
                }, 1000);

            }

        });

        /* Check the location of each desired element */
        $('.fadeInLeft').each(function (i) {

            var bottom_of_object = $(this).offset().top + $(this).outerHeight();
            var bottom_of_window = $(window).scrollTop() + $(window).height();

            /* If the object is completely visible in the window, fade it it */
            if (bottom_of_window > bottom_of_object) {

                $(this).animate({
                    'margin-left': '0',
                    'opacity': '1'
                }, 1000);

            }

        });

        /* Check the location of each desired element */
        $('.fadeInRight').each(function (i) {

            var bottom_of_object = $(this).offset().top + $(this).outerHeight();
            var bottom_of_window = $(window).scrollTop() + $(window).height();

            /* If the object is completely visible in the window, fade it it */
            if (bottom_of_window > bottom_of_object) {

                $(this).animate({
                    'margin-right': '0',
                    'opacity': '1'
                }, 1000);

            }

        });

        /* Check the location of each desired element */
        $('.fadeInTop').each(function (i) {

            var bottom_of_object = $(this).offset().top + $(this).outerHeight();
            var bottom_of_window = $(window).scrollTop() + $(window).height();

            /* If the object is completely visible in the window, fade it it */
            if (bottom_of_window > bottom_of_object) {

                $(this).animate({
                    'margin-top': '0',
                    'opacity': '1'
                }, 1000);

            }

        });

        /* Check the location of each desired element */
        $('.fadeInBottom').each(function (i) {

            var bottom_of_object = $(this).offset().top + $(this).outerHeight();
            var bottom_of_window = $(window).scrollTop() + $(window).height();

            /* If the object is completely visible in the window, fade it it */
            if (bottom_of_window > bottom_of_object) {

                $(this).animate({
                    'margin-bottom': '0',
                    'opacity': '1'
                }, 1000);

            }

        });

        /* Check the location of each desired element */
        $('.maximize').each(function (i) {

            var bottom_of_object = $(this).offset().top + $(this).outerHeight();
            var bottom_of_window = $(window).scrollTop() + $(window).height();

            /* If the object is completely visible in the window, fade it it */
            if (bottom_of_window > bottom_of_object) {

                $(this).animate({
                    'width': '100%',
                    'height': '100%',
                    'opacity': '1'
                }, 1000);

            }

        });

    });
    /* End of -+- Animations -+- */

    /* Same height recrutation steps columns */
    var sameHeightBlocks = $('.recrutation_step_column');
    var maxHeight = Math.max.apply(
            Math, sameHeightBlocks.map(function () {
                return $(this).height();
            }).get());
    sameHeightBlocks.height(maxHeight);
    /* End of same height recrutation steps columns */

    /* Same height recrutation steps columns */
    var sameHeightBlocks2 = $('.recrutation_step_title');
    var maxHeight = Math.max.apply(
            Math, sameHeightBlocks2.map(function () {
                return $(this).height();
            }).get());
    sameHeightBlocks2.height(maxHeight);
    /* End of same height recrutation steps columns */

    /* Photo slider */
    $('.meet_our_volunteers_slider').slick({
        infinite: true,
        speed: 300,
        slidesToShow: 1,
        centerMode: true,
        variableWidth: true,
        responsive: [
            {
                breakpoint: 767,
                settings: {
                    variableWidth: false
                }
            }
        ]
    });
    $('.volunteers_bulletin_slider').slick({
        infinite: true,
        speed: 300,
        slidesToShow: 2,
        centerMode: true,
        variableWidth: true,
        responsive: [
            {
                breakpoint: 767,
                settings: {
                    variableWidth: false
                }
            }
        ]
    });
    $('.the_tasks_of_volunteer_slider').slick({
        infinite: true,
        speed: 300,
        slidesToShow: 1,
        centerMode: true,
        variableWidth: true,
        responsive: [
            {
                breakpoint: 767,
                settings: {
                    variableWidth: false
                }
            }
        ]
    });
    $('.the_tasks_of_coordinator_slider').slick({
        infinite: true,
        speed: 300,
        slidesToShow: 1,
        centerMode: true,
        variableWidth: true,
        responsive: [
            {
                breakpoint: 767,
                settings: {
                    variableWidth: false
                }
            }
        ]
    });

    /* End of photo slider */

});
