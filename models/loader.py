import os
import xml.etree.ElementTree as ET

from odoo.tools.misc import file_open

class Defines:
    # In __manifest__.py
    MODULE_NAME = "export_and_shipping"

    # In views.xml
    EXPORTORDER_ACTIONS_EXTID = "exportorder_actions"
    EXPORTORDER_FORMVIEW_NAME = "exportorder.form"
    EXPORTORDER_TREEVIEW_NAME = "exportorder.tree"

class Loader:
    _tag_vendor = None
    _cat_product = None

    _update = False

    def __init__(self, shipment):
        self.environment = shipment.env

    def __enter__(self):
        pathname = os.path.join(Defines.MODULE_NAME, u'data/default_post_install.xml')
        self.fp = file_open(pathname)
        self.tree = ET.fromstring(self.fp.read())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fp.close()

    @staticmethod
    def _read_categories():
        pathname = os.path.join(Defines.MODULE_NAME, u'data/default.xml')
        fp = file_open(pathname)

        try:
            tree = ET.fromstring(fp.read())

            categories = tree.findall(".//data/record[@model='res.partner.category']")
            for category in categories:
                field = category.find(".//field[@name='name']")
                Loader._tag_vendor[category.attrib["id"]] = field.text

            categories = tree.findall(".//data/record[@model='product.category']")
            for category in categories:
                field = category.find(".//field[@name='name']")
                Loader._cat_product[category.attrib["id"]] = field.text
        finally:
            fp.close()

    @staticmethod
    def get_tag_vendor():
        if Loader._tag_vendor is None or Loader._cat_product is None:
            Loader._read_categories()
        return Loader._tag_vendor

    @staticmethod
    def get_cat_product():
        if Loader._tag_vendor is None or Loader._cat_product is None:
            Loader._read_categories()
        return Loader._cat_product

    @staticmethod
    def update_if_needed(model):
        if not Loader._update:
            return

        with Loader(model) as load:
            load.add_default_vendors()
            load.add_default_products()

        Loader._update = False

    @staticmethod
    def flag_update():
        Loader._update = True

    def add_default_vendors(self):
        res_partners = self.environment["res.partner"]

        for cat_id, cat_name in self.get_tag_vendor().iteritems():
            res_partner_category = self.environment.ref(Defines.MODULE_NAME + '.' + cat_id)
            find_nodes_xpath = ".//data/vendors/category[@id='{0}']".format(cat_id)
            cat_nodes = self.tree.findall(find_nodes_xpath)
            cat_nodes = cat_nodes[0]
            for cat_node in cat_nodes._children:
                # Would be great to use an external id, like Odoo does with its own data files,
                # to avoid a string-based query
                vendor_exists = [('name', 'ilike', cat_node.text)]
                if res_partners.search_count(vendor_exists) == 0:
                    res_partner_obj = {u'type': u'contact', u'is_company': False, u'customer': False, u'supplier': True,
                                       u'employee': False,
                                       u'name': cat_node.text, u'category_id': [(4, [res_partner_category.id])]}
                    res_partners.create(res_partner_obj)

    def add_default_products(self):
        product_templates = self.environment["product.template"]

        # Perishable category is the only one, so far, and for the foreseeable future
        cat_xmlid = Loader.get_cat_product().iterkeys().next()
        product_category = self.environment.ref(Defines.MODULE_NAME + '.' + cat_xmlid)
        find_nodes_xpath = ".//data/products/product"
        product_nodes = self.tree.findall(find_nodes_xpath)

        for product_node in product_nodes:
            # Would be great to use an external id, like Odoo does with its own data files,
            # to avoid a string-based query
            product_exists = [('name', 'ilike', product_node.attrib["name"])]
            if product_templates.search_count(product_exists) != 0:
                continue

            product_template_obj = { u'sale_ok': True, u'purchase_ok': True,
                                     u'name': product_node.attrib["name"], u'categ_id': product_category.id }
            product_template = product_templates.create(product_template_obj)

            att_val_xmlids = []
            for variety_node in product_node._children:
                att_val_xmlids.append(variety_node.attrib["id"])

            self.add_varieties(product_template, att_val_xmlids)

    def add_varieties(self, product_template, att_val_xmlids):
        if len(att_val_xmlids) <= 0:
            return

        product_products = self.environment["product.product"]
        old_product_product = product_products.search([('product_tmpl_id', '=', product_template.id)])

        for att_val_xmlid in att_val_xmlids:
            product_attribute_value = self.environment.ref(Defines.MODULE_NAME + '.' + att_val_xmlid)
            product_attribute = product_attribute_value.attribute_id

            product_attributes_lines = self.environment["product.attribute.line"]

            line_search = product_attributes_lines.search([(u'attribute_id', '=', product_attribute.id), (u'product_tmpl_id', '=', product_template.id)])
            if len(line_search) == 0:
                product_attribute_line = product_attributes_lines.create({ u'attribute_id': product_attribute.id, u'product_tmpl_id':product_template.id })
            else:
                product_attribute_line = line_search[0]

            new_product_product = product_products.create({ u'sale_ok': True, u'purchase_ok': True, u'product_tmpl_id': product_template.id,
                                         u'name': product_template.name, u'categ_id': product_template.categ_id.id })

            product_attribute_value.write({u'product_ids': [(4, [new_product_product.id])] })
            product_attribute_line.write({u'value_ids': [(4, [product_attribute_value.id])]})

        old_product_product.unlink()