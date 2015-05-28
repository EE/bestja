jQuery(window).ready(function () {
    "use strict";
    var IntroInit = function () {

        var _body = document.querySelector('body');

        var Tour = introJs();

        var _element = document.querySelector('#oe_main_menu_navbar ul.oe_user_menu_placeholder');


        Tour.setOptions({
            'doneLabel': 'OK',
            'disableInteraction': true,
            'showButtons': true,
            'showProgress': false,
            'showBullets': false,
            'exitOnEsc': false,
            'exitOnOverlayClick': false,
            'showStepNumbers': false,
            'keyboardNavigation': false,
            'steps': [
                {
                    'element': _element,
                    'intro': 'Uzupełnij swój profil!<br/> Będziemy mogli dobierać oferty zgodnie z Twoimi zainteresowaniami',
                    'position': 'bottom-right-aligned'
                }
            ]
        });
        Tour.onbeforechange(function () {
            _body.style.overflow = 'hidden';
        });
        Tour.oncomplete(function () {
            _body.style.overflow = '';
            setCookie('intro_panel_completed', 'yes', 365);
        });
        var _initIntro = function (e) {
            if (_element.style.display !== 'none') {
                Tour.start();
                _element.removeEventListener('DOMNodeInserted', _initIntro, false)
            }

        };
        _element.addEventListener('DOMNodeInserted', _initIntro, false);
    };

    if (getCookie('intro_panel_completed') !== 'yes') {
        IntroInit();
    }


});