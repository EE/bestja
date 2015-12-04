# -*- coding: utf-8 -*-
from openerp import models, fields, api


class QuestionCategory(models.Model):
    _name = 'bestja.question.category'

    name = fields.Char(required=True, string=u"Nazwa")


class Question(models.Model):
    _name = 'bestja.question'
    _inherit = [
        'protected_fields.mixin',
        'ir.needaction_mixin',
        'message_template.mixin',
    ]
    _protected_fields = ['answear', 'is_faq']
    _permitted_groups = ['bestja_base.instance_admin']

    name = fields.Char(required=True, string=u"Pytanie")
    category = fields.Many2one('bestja.question.category', required=True, string=u"Kategoria")
    question = fields.Text(string=u"Szczegóły pytania")
    screenshot = fields.Binary(string="Zrzut ekranu")
    answear = fields.Html(string=u"Odpowiedź")
    is_faq = fields.Boolean(string="Najczęściej zadawane pytanie", default=False)
    is_answeared = fields.Boolean(compute='_compute_is_answeared', store=True, string=u"Odpowiedziano")
    user_is_asker = fields.Boolean(compute='_compute_user_is_asker')
    user_is_admin = fields.Boolean(compute='_compute_user_is_admin')

    @api.one
    @api.depends('answear')
    def _compute_is_answeared(self):
        self.is_answeared = bool(self.answear)

    @api.one
    @api.depends('create_uid')
    def _compute_user_is_asker(self):
        self.user_is_asker = (self.create_uid.id == self.env.uid)

    @api.one
    def _compute_user_is_admin(self):
        self.user_is_admin = self.user_has_groups('bestja_base.instance_admin')

    @api.model
    def create(self, vals):
        record = super(Question, self).create(vals)
        record.send_group(
            template='bestja_helpdesk.msg_question_new',
            group='bestja_base.instance_admin',
        )
        return record

    @api.multi
    def write(self, vals):
        old_is_answeared = self.is_answeared
        success = super(Question, self).write(vals)
        if not old_is_answeared and self.is_answeared:
            self.send(
                template='bestja_helpdesk.msg_question_answeared',
                recipients=self.create_uid,
                sender=self.env.user,
            )
        return success

    @api.model
    def _needaction_domain_get(self):
        """
        Show unansweared count in menu - only for admins.
        """
        if not self.user_has_groups('bestja_base.instance_admin'):
            return False
        return [('is_answeared', '=', False)]
