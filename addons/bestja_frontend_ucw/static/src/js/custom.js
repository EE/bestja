jQuery(window).ready(function () {
    /* Function which changes size of Main top photo snippet when window is resized */
    var windowResize = $(window).on('resize', function () {
        var height = $(this).height() - $("navbar-static-top").height() - 50;
        $('.carousel').height(height);
    });
    /* End of function resize */

    $('#rootwizard').bootstrapWizard({'tabClass': 'nav nav-pills'});        
});

document.getElementById('category1').style.webkitFilter = 'brightness(0.4) sepia(1) hue-rotate(260deg) saturate(4)';
document.getElementById('category2').style.webkitFilter = 'brightness(0.4) sepia(1) hue-rotate(260deg) saturate(4)';
document.getElementById('category3').style.webkitFilter = 'brightness(0.4) sepia(1) hue-rotate(260deg) saturate(4)';
document.getElementById('category4').style.webkitFilter = 'brightness(0.4) sepia(1) hue-rotate(260deg) saturate(4)';