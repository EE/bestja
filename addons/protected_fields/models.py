# -*- coding: utf-8 -*-

from openerp import models, api, exceptions, SUPERUSER_ID


class ProtectedFieldsMixin(models.AbstractModel):
    """
    This Mixin allows model creators to specify a list
    of "protected fields" (`_protected_fields` property).

    Protected fields can be read by everyone with read
    permissions to the object, but can be modified
    only by users in groups listed in `_permitted_groups`
    or with ids listed in `_permitted_user_ids`.
    """
    _name = 'protected_fields.mixin'

    _protected_fields = []
    _permitted_user_ids = [SUPERUSER_ID, ]
    _permitted_groups = []

    @api.multi
    def _is_permitted(self):
        """
        Is the current user permitted to modify protected fields?

        For more advanced rules, you can modify this method in your model.
        """
        # User permissions
        if self.env.user.id in self._permitted_user_ids:
            return True

        # Group permissions
        return bool(self._permitted_groups) and self.user_has_groups(','.join(self._permitted_groups))

    @api.multi
    def _check_field_permissions(self, vals, permitted_vals=None):
        if permitted_vals is None:
            permitted_vals = {}

        if not self._is_permitted():
            for field_name in self._protected_fields:
                if field_name in vals \
                        and permitted_vals.get(field_name) != vals[field_name]:
                    raise exceptions.AccessError(
                        "You don't have permissions to modify the {} field!".format(field_name)
                    )

    @api.model
    def create(self, vals):
        # default values are permitted upon creation
        defaults = self.default_get(vals)
        record = super(ProtectedFieldsMixin, self).create(vals)
        record._check_field_permissions(vals, permitted_vals=defaults)
        return record

    @api.multi
    def write(self, vals):
        self._check_field_permissions(vals)
        success = super(ProtectedFieldsMixin, self).write(vals)
        self._check_field_permissions(vals)
        return success
