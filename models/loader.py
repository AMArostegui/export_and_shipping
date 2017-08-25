import os
import xml.etree.ElementTree as ET

from odoo.tools.misc import file_open

class Loader:
    TAG_VENDOR = {}
    CAT_PRODUCT = []

    def __init__(self, environment):
        self.environment = environment

    def __enter__(self):
        pathname = os.path.join(u'export_and_shipping', u'data/default_post_install.xml')
        self.fp = file_open(pathname)
        self.tree = ET.fromstring(self.fp.read())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fp.close()

    @staticmethod
    def read_categories():
        pathname = os.path.join(u'export_and_shipping', u'data/default.xml')
        fp = file_open(pathname)

        try:
            tree = ET.fromstring(fp.read())

            categories = tree.findall(".//data/record[@model='res.partner.category']")
            for category in categories:
                field = category.find(".//field[@name='name']")
                Loader.TAG_VENDOR[category.attrib["id"]] = field.text

            categories = tree.findall(".//data/record[@model='product.category']")
            for category in categories:
                field = category.find(".//field[@name='name']")
                Loader.CAT_PRODUCT.append(field.text)
        finally:
            fp.close()

    def add_default_vendors(self):
        res_partners = self.environment["res.partner"]
        res_partners_categories = self.environment["res.partner.category"]

        for cat_id, cat_name in Loader.TAG_VENDOR.iteritems():
            category = res_partners_categories.search([('name', 'ilike', cat_name)])
            find_nodes_xpath = ".//data/vendors/category[@id='{0}']".format(cat_id)
            cat_nodes = self.tree.findall(find_nodes_xpath)
            cat_nodes = cat_nodes[0]
            for cat_node in cat_nodes._children:
                new_partner = { u'type': u'contact', u'is_company': False, u'customer': False, u'supplier': True, u'employee': False,
                               u'name': cat_node.text, u'category_id': [(4, [category.id])] }
                domain_check_exists = [('name', 'ilike', new_partner['name'])]
                if res_partners.search_count(domain_check_exists) == 0:
                    res_partners.create(new_partner)

    def add_default_products(self):
        product_template = self.environment["product.template"]
        product_category = self.environment["product.category"]
        cat_id = product_category.search([('name', 'ilike', Loader.CAT_PRODUCT[0])])

        find_nodes_xpath = ".//data/products/product"
        product_nodes = self.tree.findall(find_nodes_xpath)

        for product_node in product_nodes:
            new_product_template = { u'sale_ok': True, u'purchase_ok': True,
                                     u'name': product_node.attrib["name"], u'categ_id': cat_id.id }
            domain_check_exists = [('name', 'ilike', new_product_template['name'])]
            if product_template.search_count(domain_check_exists) != 0:
                continue

            product_template.create(new_product_template)