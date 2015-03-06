# -*- coding: utf-8 -*-
from openerp import models, fields, api


class Project(models.Model):
    _inherit = 'bestja.project'

    request_template = fields.Many2one(
        'bestja_requests.template',
        string=u"Szablon zapotrzebowań",
        domain="[('organization', '=', organization)]",
        ondelete='restrict',
    )
    requests = fields.One2many('bestja_requests.request', inverse_name='project')

    @api.model
    def create(self, vals):
        record = super(Project, self).create(vals)
        if record.parent.request_template:
            record.send(
                template='bestja_requests.msg_call_for_requests',
                recipients=record.responsible_user,
            )
        return record

    @api.multi
    def write(self, vals):
        old_request_template = self.request_template
        success = super(Project, self).write(vals)
        if not old_request_template and self.request_template:
            for child in self.sudo().children:
                child.send(
                    template='bestja_requests.msg_call_for_requests',
                    recipients=child.responsible_user,
                )
        return success


class RequestTemplateItem(models.Model):
    _name = 'bestja_requests.template_item'

    name = fields.Char(required=True, string=u"nazwa")
    template = fields.Many2one(
        'bestja_requests.template',
        required=True,
        string=u"szablon",
        ondelete='cascade',
    )


class RequestTemplate(models.Model):
    _name = 'bestja_requests.template'

    @api.model
    def _default_organization(self):
        return self.env.user.coordinated_org

    name = fields.Char(required=True, string=u"nazwa")
    organization = fields.Many2one(
        'organization',
        required=True,
        domain="['|', ('coordinator', '=', uid), ('projects.manager', '=', uid)]",
        string=u"organizacja",
        default=_default_organization,
        ondelete='restrict',
    )
    items = fields.One2many('bestja_requests.template_item', inverse_name='template')
    projects = fields.One2many('bestja.project', inverse_name='request_template')

    @api.multi
    def copy(self, default=None):
        """
        When coping a request template, also copy its items.
        """
        new_obj = super(RequestTemplate, self).copy(default)
        for item in self.items:
            item.copy(default={'template': new_obj.id})
        return new_obj


class RequestItem(models.Model):
    _name = 'bestja_requests.item'

    request = fields.Many2one(
        'bestja_requests.request',
        ondelete='cascade',
        required=True,
    )
    template = fields.Many2one(
        'bestja_requests.template',
        compute='compute_template',
    )
    template_item = fields.Many2one(
        'bestja_requests.template_item',
        domain="[('template', '=', template)]",
        required=True,
        string=u"element",
        ondelete='restrict',
    )
    parent_project = fields.Many2one(
        'bestja.project',
        string=u"Projekt nadrzędny",
        store=True,  # Needed by graph view
        related='request.parent_project',
    )
    organization = fields.Many2one(
        'organization',
        string=u"Organizacja",
        store=True,
        related='request.project.organization',
    )
    quantity = fields.Integer(required=True, string=u"ilość")

    _sql_constraints = [
        ('request_item_uniq', 'unique("request", "template_item")', "Dany element można wybrać tylko raz!")
    ]

    @api.one
    @api.depends('request')
    def compute_template(self):
        # Note: You'd normally do this using a related field, instead of an
        # explicit computed field.
        #
        # Unfortunately in this case that's not possible because:
        #
        # 1. When the request form is being edited `self` and `self.request`
        # are in a draft mode (which means their content is sourced from
        # the form that is being edited, and not strictly from the db).
        #
        # 2. Related fields are normally computed with super admin privileges,
        # unfortunately that's not the case with records in draft mode.
        # When a record is in draft mode the `related_sudo` is completely ignored
        # and the field is always evaluated with the current user privileges.
        # See also: https://github.com/odoo/odoo/issues/5121
        #
        # 3. That's a problem for us, because `self.request.project` in some cases
        # may not be accessible by the current user (if she's a coordinator of a
        # parent organization). And we need to get through `self.request.project`
        # to get to `request_template`.
        #
        # ---
        #
        # You should also note the importance of the exact placement of sudo() in
        # the code below. You can not use sudo() with records in draft mode, because
        # they only exist in the current environment, and sudo() creates a new
        # environment. In this case this means that you shouldn't put sudo()
        # directly after `self` or `request`. You can put sudo() after `project`,
        # which is not in draft mode, even though it may not be accessible to the
        # current user, because the read will be performed only when we try
        # to access one of its fields (`parent` in this particular case).
        #
        # That's also why we can't just use the `request.parent_project` related field,
        # even though it is stored and has a precomputed value already. Stored
        # fields are always computed from scratch on draft records and (as we already know),
        # the automatic computation of related fields on draft records ignores the
        # `sudo_related` option.
        #
        # Thank you for your attention. Have a nice day.
        self.template = self.request.project.sudo().parent.request_template


class Request(models.Model):
    _name = 'bestja_requests.request'
    _inherit = [
        'protected_fields.mixin',
        'ir.needaction_mixin',
        'message_template.mixin',
    ]
    _order = 'write_uid desc'
    STATES = [
        ('draft', 'szkic'),
        ('pending', 'oczekujące'),
        ('accepted', 'zaakceptowane'),
        ('rejected', 'odrzucone'),
    ]
    _protected_fields = ['state']

    state = fields.Selection(STATES, default='draft', string=u"Stan")
    name = fields.Char(
        string=u"nazwa",
        related='project.name',
        store=True,
    )
    project = fields.Many2one(
        'bestja.project',
        domain="""[
            ('parent.request_template', '!=', False),
            ('requests', '=', False),
            '|',
                ('manager', '=', uid),
                ('organization.coordinator', '=', uid),
        ]""",
        required=True,
        string=u"Projekt",
        ondelete='restrict',
    )
    items = fields.One2many('bestja_requests.item', inverse_name='request')
    comments = fields.Text(string=u"Uwagi")
    manager = fields.Many2one(
        'res.users',
        string=u"Menadżer projektu",
        related='project.responsible_user',
    )
    manager_phone = fields.Char(
        string=u"Telefon menadżera",
        related='project.responsible_user.phone',
    )
    organization = fields.Many2one(
        'organization',
        string=u"Organizacja",
        related='project.organization'
    )
    parent_project = fields.Many2one(
        'bestja.project',
        string=u"Projekt nadrzędny",
        related='project.parent',
        store=True,
    )
    user_can_moderate = fields.Boolean(compute="_compute_user_can_moderate")

    @api.one
    @api.depends('parent_project')
    def _compute_user_can_moderate(self):
        """
        Is current user authorized to moderate (accept/reject) the request?
        """
        project = self.sudo().project
        self.user_can_moderate = (
            project.parent.manager.id == self.env.uid or
            project.parent.organization.coordinator.id == self.env.uid
        )

    @api.multi
    def continue_action(self):
        """
        Action for the "continue" button on the form. The button is intended
        to force saving the object and doesn't currently do anything
        in addition to that.
        """
        pass

    @api.one
    def set_pending(self):
        self.sudo().state = 'pending'
        self.send(
            template='bestja_requests.msg_request_pending',
            recipients=self.parent_project.responsible_user,
            record_name=self.organization.name,
        )

    @api.one
    def set_accepted(self):
        self.state = 'accepted'

    @api.one
    def set_rejected(self):
        self.state = 'rejected'
        self.send(
            template='bestja_requests.msg_request_rejected',
            recipients=self.sudo().project.responsible_user,
            sender=self.env.user,
        )

    @api.multi
    def _is_permitted(self):
        """
        Allow authorized users to modify protected fields
        """
        permitted = super(Request, self)._is_permitted()
        return permitted or self.user_can_moderate

    @api.model
    def _needaction_domain_get(self):
        """
        Show pending count in menu.
        """
        return [
            ('state', '=', 'pending'),
        ]
