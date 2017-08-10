# -*- coding: utf-8 -*-

from odoo import models, fields

class Shipment(models.Model):
    _name = 'export_and_shipping.shipment'

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
        domain=['&', ('supplier', '=', True), ('category_id.name', 'ilike', "Forwarder")])

    transport = fields.Many2one('res.partner',
        ondelete='set null', string="Transport", index=True, required=True,
        domain = ['&', ('supplier', '=', True), ('category_id.name', 'ilike', "Transport")])
