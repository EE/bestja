jQuery(window).ready(function () {
    "use strict";

    var _el = document.querySelector('.dropdown.intro_tour_front');

    var IntroInit = function () {

        var _body = document.querySelector('body');

        var Tour = introJs();
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
                    'element': _el,
                    'intro': 'Wybierz z listy "Przejdź do aplikacji", aby zobaczyć wiadomości i swoje zadania',
                    'position': 'bottom-right-aligned'
                }
            ]
        });
        Tour.onbeforechange(function(){
            _body.style.overflow = 'hidden';
        });
        Tour.oncomplete(function(){
            _body.style.overflow = 'visible';
            setCookie('intro_front_completed', 'yes', 365);
        });
        Tour.start();
    };

    if(getCookie('intro_front_completed') !== 'yes' && _el){
        IntroInit();
    }




});