# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.addons.export_and_shipping.models import loader

class Shipment(models.Model):
    _name = 'export_and_shipping.shipment'

    _startup = False

    departure_dt = fields.Datetime(string="Departure", default=fields.Datetime.now())
    arrival_dt = fields.Datetime(string="Arrival", default=fields.Datetime.now())

    order_id = fields.One2many("sale.order", "shipment_id", string="Export Orders", ondelete="set null", index=True)

    flight_no = fields.Char(string="Flight / Container Number")
    by_plane = fields.Boolean(string="By Plane", default=True)

    # Would be great to get rid of those "ilike" domains, and simply use database ids
    transport = fields.Many2one('res.partner',
        ondelete='set null', string="Transport", index=True, required=True,
        domain = ['&', ('supplier', '=', True), ('category_id.name', 'ilike', loader.Loader.get_tag_vendor()["TagTransporter"])])

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

    awb = fields.Char(string="Airway Bill / Book")

    forwarder = fields.Many2one('res.partner',
        ondelete='set null', string="Forwarder", index=True,
        domain=['&', ('supplier', '=', True), ('category_id.name', 'ilike', loader.Loader.get_tag_vendor()["TagForwarder"])])

    to_export = fields.Boolean(string="Export Order", default=False)

    shipment_id = fields.Many2one('export_and_shipping.shipment', string='Shipment Reference', index=True, copy=False)

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        new_view_id = view_id

        # This is a hack to show inherited view from sales.order only after clicking on our own menuitem
        if view_id is None:
            view_name = ""
            if view_type == "form":
                view_name = loader.Defines.EXPORTORDER_FORMVIEW_NAME
            elif view_type == "tree":
                view_name = loader.Defines.EXPORTORDER_TREEVIEW_NAME

            if view_name and self.is_model_action():
                ir_ui_view = self.env['ir.ui.view']
                domain = [('name', '=', view_name)]
                new_view_id = ir_ui_view.search(domain, limit=1).id

        return super(SaleOrder, self).fields_view_get(view_id=new_view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
    @api.model
    def create(self, vals):
        if self.is_model_action():
            vals["to_export"] = True
        return super(SaleOrder, self).create(vals=vals)

    def is_model_action(self):
        if "params" in self.env.context and "action" in self.env.context["params"]:
            action_dbid = self.env.context["params"]["action"]
            action = self.env.ref(loader.Defines.MODULE_NAME + "." + loader.Defines.EXPORTORDER_ACTIONS_EXTID)
            if action.id == action_dbid:
                return True
        return False

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    retrieval_date = fields.Date(string="Retrieval", default=fields.Date.today)

    size = fields.Integer(string="Product Size")
    is_organic = fields.Boolean(string="Is Organic", default=False)
    quality = fields.Selection(string="Quality", selection=[('CATI', 'Cat I'), ('CATII', 'Cat II'), ('CATIII', 'Cat III')])

    is_export_order = fields.Boolean(related="order_id.to_export")