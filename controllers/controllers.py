# -*- coding: utf-8 -*-
from odoo import http

# class ExportAndShipping(http.Controller):
#     @http.route('/export_and_shipping/export_and_shipping/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/export_and_shipping/export_and_shipping/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('export_and_shipping.listing', {
#             'root': '/export_and_shipping/export_and_shipping',
#             'objects': http.request.env['export_and_shipping.export_and_shipping'].search([]),
#         })

#     @http.route('/export_and_shipping/export_and_shipping/objects/<model("export_and_shipping.export_and_shipping"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('export_and_shipping.object', {
#             'object': obj
#         })