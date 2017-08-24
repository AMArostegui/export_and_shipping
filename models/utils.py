import os
import xml.etree.ElementTree as ET

from odoo.tools.misc import file_open

CAT_VENDOR = ["Grower", "Transport and Logistics", "Forwarder"]

def add_default_vendors(res_partners, res_partners_categories):
    pathname = os.path.join(u'export_and_shipping', u'data/default_post_install.xml')
    fp = file_open(pathname)
    try:
        tree = ET.fromstring(fp.read())

        for cat_pos in range(0, len(CAT_VENDOR)):
            category = res_partners_categories.search([('name', 'ilike', CAT_VENDOR[cat_pos])])
            find_nodes_xpath = ".//data/vendors/category[@id='{0}']".format(cat_pos)
            cat_nodes = tree.findall(find_nodes_xpath)
            cat_nodes = cat_nodes[0]
            for cat_node in cat_nodes._children:
                new_partner = { u'type': u'contact', u'is_company': False, u'customer': False, u'supplier': True, u'employee': False,
                               u'name': cat_node.text, u'category_id': [(4, [category.id])] }
                domain_check_exists = [('name', 'ilike', new_partner['name'])]
                if res_partners.search_count(domain_check_exists) == 0:
                    res_partners.create(new_partner)
    finally:
        fp.close()

def add_default_products(product_template, product_product, product_price_history):
    pathname = os.path.join(u'export_and_shipping', u'data/default_post_install.xml')
    fp = file_open(pathname)
    try:
        tree = ET.fromstring(fp.read())

        find_nodes_xpath = ".//data/products/product"
        product_nodes = tree.findall(find_nodes_xpath)
        for product_node in product_nodes:
            new_product_template = { u'sale_ok': True, u'purchase_ok': True, u'name': product_node.attrib["name"] }
            domain_check_exists = [('name', 'ilike', new_product_template['name'])]
            if product_template.search_count(domain_check_exists) != 0:
                continue

            product_template.create(new_product_template)
    finally:
        fp.close()
