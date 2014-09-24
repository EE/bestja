# -*- coding: utf-8 -*-
# from openerp import http

# class Volunteer(http.Controller):
#     @http.route('/volunteer/', auth='user', website=True)
#     def profile(self, **kw):
#         return http.request.render('bestja_volunteer.profile', {
#             'volunteers': http.request.env.user.employee_ids,
#         })

# @http.route('/volunteer/volunteer/objects/', auth='public')
# def list(self, **kw):
#     return http.request.render('volunteer.listing', {
#         'root': '/volunteer/volunteer',
#         'objects': http.request.env['volunteer.volunteer'].search([]),
#     })

# @http.route('/volunteer/volunteer/objects/<model("volunteer.volunteer"):obj>/', auth='public')
# def object(self, obj, **kw):
#     return http.request.render('volunteer.object', {
#         'object': obj
#     })
