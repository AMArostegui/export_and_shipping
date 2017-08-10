# -*- coding: utf-8 -*-

from odoo import models, fields

class Shipment(models.Model):
    _name = 'export_and_shipping.shipment'

    awb = fields.Char(string="Airway Bill")
    date = fields.Date(string="Departure", default=fields.Date.today)
    by_plane = fields.Boolean(string="By Plane", default=True)

    perishable = fields.Many2one('product.product',
        ondelete='set null', string="Perishable", index=True)
