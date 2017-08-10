# -*- coding: utf-8 -*-

from odoo import models, fields

class Shipment(models.Model):
    _name = 'export_and_shipping.shipment'

    awb = fields.Char(string="Airway Bill / Book")
    date = fields.Date(string="Departure", default=fields.Date.today)
    by_plane = fields.Boolean(string="By Plane", default=True)

    perishable = fields.Many2one('product.product',
        ondelete='set null', string="Perishable", index=True)

    forwarder = fields.Many2one('res.partner',
        ondelete='set null', string="Forwarder", index=True,
        domain=['&', ('supplier', '=', True), ('category_id.name', 'ilike', "Forwarder")])

    transport = fields.Many2one('res.partner',
        ondelete='set null', string="Transport", index=True, required=True,
        domain = ['&', ('supplier', '=', True), ('category_id.name', 'ilike', "Transport")])
