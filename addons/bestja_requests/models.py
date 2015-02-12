# -*- coding: utf-8 -*-
from openerp import models, fields, api


class Project(models.Model):
    _inherit = 'bestja.project'

    request_template = fields.Many2one(
        'bestja_requests.template',
        string="Szablon zapotrzebowań",
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

    name = fields.Char(required=True, string="nazwa")
    template = fields.Many2one(
        'bestja_requests.template',
        required=True,
        string="szablon",
        ondelete='cascade',
    )


class RequestTemplate(models.Model):
    _name = 'bestja_requests.template'

    @api.model
    def _default_organization(self):
        return self.env.user.coordinated_org

    name = fields.Char(required=True, string="nazwa")
    organization = fields.Many2one(
        'organization',
        required=True,
        domain="['|', ('coordinator', '=', uid), ('projects.manager', '=', uid)]",
        string="organizacja",
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
    template_item = fields.Many2one(
        'bestja_requests.template_item',
        domain="[('template.projects', '=', parent_project)]",
        required=True,
        string="element",
        ondelete='restrict',
    )
    parent_project = fields.Many2one(
        'bestja.project',
        string="Projekt nadrzędny",
        store=True,  # Needed by graph view
        related='request.parent_project',
    )
    organization = fields.Many2one(
        'organization',
        string="Organizacja",
        store=True,
        related='request.project.organization',
    )
    quantity = fields.Integer(required=True, string="ilość")

    _sql_constraints = [
        ('request_item_uniq', 'unique("request", "template_item")', "Dany element można wybrać tylko raz!")
    ]


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

    state = fields.Selection(STATES, default='draft', string="Stan")
    name = fields.Char(
        string="nazwa",
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
        string="Projekt",
        ondelete='restrict',
    )
    items = fields.One2many('bestja_requests.item', inverse_name='request')
    comments = fields.Text(string="uwagi")
    manager = fields.Many2one(
        'res.users',
        string="Menadżer projektu",
        related='project.responsible_user',
    )
    manager_phone = fields.Char(
        string="Telefon menadżera",
        related='project.responsible_user.phone',
    )
    organization = fields.Many2one(
        'organization',
        string="Organizacja",
        related='project.organization'
    )
    parent_project = fields.Many2one(
        'bestja.project',
        string="Projekt nadrzędny",
        related='project.parent',
        store=True,
    )
    user_can_moderate = fields.Boolean(compute="compute_user_can_moderate")

    @api.one
    @api.depends('parent_project')
    def compute_user_can_moderate(self):
        """
        Is current user authorized to moderate (accept/reject) the request?
        """
        self.user_can_moderate = (
            self.parent_project.manager.id == self.env.uid or
            self.parent_project.organization.coordinator.id == self.env.uid
        )

    @api.multi
    def continue_action(self):
        """
        Action for the "continue" button on the form. The button is intended
        to force saving the object and doesn't currently do anything
        in addition to that.
        """
        pass

    @api.multi
    def set_pending(self):
        self.sudo().state = 'pending'
        self.send(
            template='bestja_requests.msg_request_pending',
            recipients=self.parent_project.responsible_user,
            record_name=self.organization.name,
        )

    @api.multi
    def set_accepted(self):
        self.state = 'accepted'

    @api.multi
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
