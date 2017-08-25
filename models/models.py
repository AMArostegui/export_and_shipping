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

    loader.Loader.read_categories()

    forwarder = fields.Many2one('res.partner',
        ondelete='set null', string="Forwarder", index=True,
        domain=['&', ('supplier', '=', True), ('category_id.name', 'ilike', loader.Loader.TAG_VENDOR["TagForwarder"])])

    transport = fields.Many2one('res.partner',
        ondelete='set null', string="Transport", index=True, required=True,
        domain = ['&', ('supplier', '=', True), ('category_id.name', 'ilike', loader.Loader.TAG_VENDOR["TagTransporter"])])

    notes = fields.Char(string="Notes")

    @api.model
    def view_init(self, fields_list):
        model_product_template = self.env["product.template"]
        product_template = model_product_template.search([('name', 'ilike', "Mango")])

        model_product_product = self.env["product.product"]
        old_product_product = model_product_product.search([('name', 'ilike', "Mango")])

        model_product_attribute = self.env["product.attribute"]
        product_attribute = model_product_attribute.search([('name', 'ilike', "Tipo Mango")])

        model_product_attributes_line = self.env["product.attribute.line"]
        product_attribute_line = model_product_attributes_line.create({ u'attribute_id': product_attribute.id, u'product_tmpl_id':product_template.id })

        model_product_attribute_value = self.env["product.attribute.value"]

        new_product_product = model_product_product.create({ u'sale_ok': True, u'purchase_ok': True, u'product_tmpl_id': product_template.id,
                                     u'name': product_template.name, u'categ_id': product_template.categ_id.id })
        product_attribute_value = model_product_attribute_value.search([('name', 'ilike', "Keitt")])
        product_attribute_value.write({u'product_ids': [(4, [new_product_product.id])] })
        kaka = [(4, [new_product_product.id])]

        new_product_product = model_product_product.create({ u'sale_ok': True, u'purchase_ok': True, u'product_tmpl_id': product_template.id,
                                     u'name': product_template.name, u'categ_id': product_template.categ_id.id })
        product_attribute_value = model_product_attribute_value.search([('name', 'ilike', "Kentt")])
        product_attribute_value.write({u'product_ids': [(4, [new_product_product.id])] })
        kaka.append((4, [new_product_product.id]))

        product_attribute_line.write({ u'value_ids': kaka })
        old_product_product.unlink()

        pass



        # if not Shipment._startup:
        #     return
        #
        # with loader.Loader(self.env) as load:
        #     load.add_default_vendors()
        #     load.add_default_products()
        #
        # Shipment._startup = False

    @api.model
    def flag_module_startup(self):
        Shipment._startup = True