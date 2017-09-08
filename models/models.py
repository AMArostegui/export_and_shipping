# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.addons.export_and_shipping.models import loader

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

    loader.Loader.read_categories(_name)

    # Would be great to get rid of those "ilike" domains, and simply use database ids
    forwarder = fields.Many2one('res.partner',
        ondelete='set null', string="Forwarder", index=True,
        domain=['&', ('supplier', '=', True), ('category_id.name', 'ilike', loader.Loader.TAG_VENDOR["TagForwarder"])])

    transport = fields.Many2one('res.partner',
        ondelete='set null', string="Transport", index=True, required=True,
        domain = ['&', ('supplier', '=', True), ('category_id.name', 'ilike', loader.Loader.TAG_VENDOR["TagTransporter"])])

    notes = fields.Char(string="Notes")

    @api.model
    def view_init(self, fields_list):
        if not Shipment._startup:
            return

        with loader.Loader(self) as load:
            load.add_default_vendors()
            load.add_default_products()

        Shipment._startup = False

    @api.model
    def flag_module_startup(self):
        Shipment._startup = True

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    to_export = fields.Boolean(string="Export Order", default=False)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    size = fields.Integer(string="Product Size")
    is_organic = fields.Boolean(string="Is Organic", default=False)
    quality = fields.Selection(string="Quality", selection=[('CATI', 'Cat I'), ('CATII', 'Cat II'), ('CATIII', 'Cat III')])
    is_export_order = fields.Boolean(related="order_id.to_export")