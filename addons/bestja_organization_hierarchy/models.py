# -*- coding: utf-8 -*-
from lxml import etree

from openerp import models, fields, api, exceptions, SUPERUSER_ID


class Organization(models.Model):
    _inherit = 'organization'
    _parent_name = 'parent'

    def allowed_parents(self):
        if self.env['res.users'].has_group('bestja_base.instance_admin'):
            return [('level', '<=', 1)]
        return [('level', '=', 1)]

    parent = fields.Many2one(
        'organization',
        domain=allowed_parents,
        string="Organizacja nadrzędna",
    )
    level = fields.Integer(
        compute='_compute_level',
        store=True,
        string="Poziom w hierarchii organizacji"
    )

    @api.one
    @api.depends('parent', 'parent.parent')
    def _compute_level(self):
        """
        Level of organization hierarchy. 0 = root level.
        """
        if not self.parent:
            self.level = 0
        else:
            self.level = self.parent.level + 1

    @api.one
    @api.constrains('parent')
    def _check_parent(self):
        """
        Only super admin is able to add primary (parentless) organizations.
        """
        if self.env.user.id == SUPERUSER_ID:
            return
        if not self.parent:
            raise exceptions.ValidationError("Wybierz organizację nadrzędną!")

    @api.multi
    def is_parent_coordinator(self):
        """
        Is the current user a coordinator of an parent organization?
        """
        return self.parent.id == self.env.user.coordinated_org.id

    @api.model
    def _is_permitted(self):
        """
        Allow parent coordinators to modify protected fields
        """
        permitted = super(Organization, self)._is_permitted()
        return permitted or self.is_parent_coordinator()

    @api.model
    def fields_view_get(self, **kwargs):
        """
        Show header buttons to parent coordinators.
        """
        view = super(Organization, self).fields_view_get(**kwargs)
        if 'view_type' in kwargs and kwargs['view_type'] != 'form':
            return view

        doc = etree.XML(view['arch'])

        # Only coordinators and admins should see moderation buttons
        # TODO: because of the issue with conditional hiding
        # of view buttons, for now coordinators see those buttons
        # for ALL organizations - not only those they can moderate.
        if not (self.env.user.coordinated_org
                or self.env['res.users'].has_group('bestja_base.instance_admin')):
            buttons = doc.xpath("//header/button")
            for button in buttons:
                button.getparent().remove(button)

        view['arch'] = etree.tostring(doc)
        return view

    @api.one
    def send_registration_messages(self):
        self.send(
            template='bestja_organization.msg_registered',
            recipients=self.coordinator,
        )
        if self.parent:
            self.send(
                template='bestja_organization.msg_registered_admin',
                recipients=self.parent.coordinator,
            )
