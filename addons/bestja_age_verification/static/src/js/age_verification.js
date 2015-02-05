'use strict';

var AgeVerification = {
    init: function() {
        /* If read only mode - abort */
        if(AgeVerification.is_form_readonly()) return;

        AgeVerification.min_age = +$('.field-birthdate').data('min-age');
        AgeVerification.block_submit(true);
        $('.field-birthdate input').keyup(AgeVerification.go_next);
        $('.field-birthdate input').keyup(AgeVerification.verify);
    },

    verify: function(event) {
        var day = $('#birthdate_day').val();
        var month = $('#birthdate_month').val()
        var year = $('#birthdate_year').val();

        if(+day && +month && +year && year.length == 4) {
            var date = new Date(year, month-1, day);
            console.log(AgeVerification.min_age);
            if(AgeVerification.is_older_than(date, AgeVerification.min_age)) {
                // Good to go :)
                AgeVerification.show_error(false);
                AgeVerification.block_submit(false);
            } else {
                // Too young
                AgeVerification.show_error(true);
                AgeVerification.block_submit(true);
            }
        } else {
            // Not filled out properly yet
            AgeVerification.block_submit(true);
            AgeVerification.show_error(false);
        }
    },

    is_older_than: function(date, age) {
        /*
        Is number of years between `date` and now larger than `age`?
        */
        var now = new Date();
        var diff_years = now.getFullYear() - date.getFullYear();
        if(diff_years > age) return true;
        if(diff_years < age) return false;

        var diff_months = now.getMonth() - date.getMonth();
        if(diff_months > 0) return true;
        if(diff_months < 0) return false;

        var diff_days = now.getDate() - date.getDate();
        if(diff_days >= 0) return true;
        return false;
    },

    is_form_readonly: function(date, age) {
        /*
        Signup form can be used in read-only mode (for example while changing password).
        Detect that.
        */
        var day_ro = $('#birthdate_day').prop('readonly');
        var month_ro = $('#birthdate_month').prop('readonly');
        var year_ro = $('#birthdate_year').prop('readonly');

        if(day_ro || month_ro || year_ro) return true;
        return false;
    },

    show_error: function(show) {
        /* show / hide form error */
        var $field = $('.field-birthdate')
        if(show) {
            $field.addClass('has-error');
        } else {
            $field.removeClass('has-error');
        }
    },

    block_submit: function(block) {
        /*  disallow / allow the form to be submitted */
        $( ".oe_signup_form button").prop( "disabled", block);
    },

    go_next: function(event) {
        /*
        Move focus to the next input after this one has been filled out.
        */
        if (this.value.length == this.maxLength) {
            $(this).next('.field-birthdate input').focus();
        }
    }
};
$(document).ready(AgeVerification.init);
