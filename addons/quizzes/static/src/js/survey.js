(function() {
    var website = openerp.website;

    function hideStateElements($container) {
        $container.find('.ee_quiz_result').text('');
    }
    website.snippet.animationRegistry.survey_snippet = website.snippet.Animation.extend({
        selector: '.survey',
        start: function (editable_mode) {
            function displayResult(val) {
                var s = val? 'Prawidłowa' : 'Błędna';

                $('<span>')
                    .text(s)
                    .addClass('label label-' + (val? 'success' : 'danger'))
                    .appendTo($el.find('.ee_quiz_result'));
            }

            var $el = this.$el;

            var answerCount = $el.find('.ee_answers').data('answer_count');
            var trials = 0;

            hideStateElements($el);

            if (!editable_mode) {
                $el.find('.ee_answer').on('click', function (e) {
                    if ($(this).data('answered')) {
                        return;
                    }
                    if (trials < answerCount) {
                        displayResult(checkCorrect(this));
                        trials++;
                    }
                    $(this).data('answered', true);
                });

                function checkCorrect(el) {
                    return $(el).closest('.ee_answer_row').find('.ee_checkbox').hasClass('ee_checkbox_active');
                }

                $el.find('.ee_answer_text').on('click', function () {
                    $(this).prev().trigger('click');
                });
            } else {
                $el.find('.ee_result').show();
            }
        }
    });

    website.snippet.options.survey_snippet = website.snippet.Option.extend({
        selector: '.survey',
        clean_for_save: function () {
            this.$target.find('.ee_result').each(function () {
                var result = $(this).text();
                $(this).prev().attr('data-answer-result', result);
                $(this).hide();

            });
            this.$target.find('.ee_onlyeditmode').hide();
            this.$target.find('.ee_onlynormalmode').show();
        },
        start: function () {
            var $target = this.$target;
            $target.find('.ee_onlyeditmode').show();
            $target.find('.ee_onlynormalmode').hide();
            var checkboxes = this.$target.find('.ee_checkbox');
            checkboxes.off();
            checkboxes.unbind();
            checkboxes.on('click', function (e) {
                $(this).toggleClass('ee_checkbox_active');
                e.preventDefault();
            });

            this.$target.find('[ee_contenteditable]').each(function () {
                var val = $(this).attr('ee_contenteditable');
                $(this).attr('contenteditable', val);
            });
        }
    });
})();
