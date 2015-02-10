jQuery(window).ready(function () {
    /* Function which changes size of Main top photo snippet when window is resized */
    var windowResize = $(window).on('resize', function () {
        var height = $(this).height() - $("navbar-static-top").height() - 50;
        if(height > 1920){
            $('.carousel').height(1080);
        } else {
            $('.carousel').height(height);
        }
    });    
    /* End of function resize */    
});
