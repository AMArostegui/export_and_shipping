# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.addons.export_and_shipping.models import utils

class Shipment(models.Model):
    _name = 'export_and_shipping.shipment'

    _startup = False

    awb = fields.Char(string="Airway Bill / Book")
    flight_no = fields.Char(string="Flight / Container Number")
    by_plane = fields.Boolean(string="By Plane", default=True)

    approx_weight = fields.Integer(string="Approx. Weight")

    retrieval_date = fields.Date(string="Retrieval", default=fields.Date.today)
    departure_date = fields.Date(string="Departure", default=fields.Date.today)
    arrival_date = fields.Date(string="Arrival", default=fields.Date.today)

    perishable = fields.Many2one('product.product',
        ondelete='set null', string="Perishable", index=True)

    customer = fields.Many2one('res.partner',
        ondelete='set null', string="Customer", index=True,
        domain=[('customer', '=', True)])

    forwarder = fields.Many2one('res.partner',
        ondelete='set null', string="Forwarder", index=True,
        domain=['&', ('supplier', '=', True), ('category_id.name', 'ilike', utils.CAT_VENDOR[2])])

    transport = fields.Many2one('res.partner',
        ondelete='set null', string="Transport", index=True, required=True,
        domain = ['&', ('supplier', '=', True), ('category_id.name', 'ilike', utils.CAT_VENDOR[1])])

    notes = fields.Char(string="Notes")

    @api.model
    def view_init(self, fields_list):
        if not Shipment._startup:
            return

        utils.add_post_install_data(self.env["res.partner"], self.env["res.partner.category"])

    @api.model
    def flag_module_startup(self):
        Shipment._startup = True