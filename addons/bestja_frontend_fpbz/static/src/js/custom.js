jQuery(window).ready(function () {



    // Background picture will fit viewport


    /* Function which changes size of Main top photo snippet when window is resized */
    var $window = $(window).on('resize', function () {
        var height = $(this).height() - $("navbar-static-top").height() - 250;

        if (height > 1080) {
            $('.introduction').height(1080 - 250);
        } else {
            $('.introduction').height(height);
        }
        /* Footer at bottom of the page */
        $('main').css('height','auto');
        $('main').height($('#wrapwrap').height() - $('footer').height() - 51);
        /* End of footer at bottom of the page */
    });
    /* End of function resize */

    $('.choose_place').click(function () {
        $('html, body').animate({
            scrollTop: $("#choose_place_title").offset().top
        }, 800);
    });

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


    /* Footer at bottom of the page */
    $('main').height($('#wrapwrap').height() - $('footer').height() - 51);
    /* End of footer at bottom of the page */
});
