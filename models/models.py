# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.addons.export_and_shipping.models import loader

MODULE_NAME = ""

def get_module_name(model_name):
    idx = model_name.find(".")
    module_name = model_name[:idx]
    return module_name

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

    global MODULE_NAME
    MODULE_NAME = get_module_name(_name)
    loader.Loader.read_categories(MODULE_NAME)

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

    EXPORTORDER_ACTIONS_EXTID = "exportorder_actions"
    EXPORTORDER_FORM_NAME = "exportorder.form"

    to_export = fields.Boolean(string="Export Order", default=False)

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        new_view_id = view_id

        # This is a hack to show inherited view from sales.order only after clicking on our own menuitem
        if view_id is None:
            if view_type == "form" and "params" in self.env.context and "action" in self.env.context["params"]:
                action_dbid = self.env.context["params"]["action"]
                action = self.env.ref(MODULE_NAME + "." + self.EXPORTORDER_ACTIONS_EXTID)
                if action.id == action_dbid:
                    ir_ui_view = self.env['ir.ui.view']
                    domain = [('name', '=', self.EXPORTORDER_FORM_NAME)]
                    new_view_id = ir_ui_view.search(domain, limit=1).id

        return super(SaleOrder, self).fields_view_get(view_id=new_view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    size = fields.Integer(string="Product Size")
    is_organic = fields.Boolean(string="Is Organic", default=False)
    quality = fields.Selection(string="Quality", selection=[('CATI', 'Cat I'), ('CATII', 'Cat II'), ('CATIII', 'Cat III')])
    is_export_order = fields.Boolean(related="order_id.to_export")