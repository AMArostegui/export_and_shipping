# -*- coding: utf-8 -*-
{
    'name': "ExportAndShipping",

    'summary': """
        Integrated perishable food exporting system""",

    'description': """
        Integrated perishable food exporting system. Manage orders, shipments and more.
    """,

    'author': "Ferba Technology",
    'website': "http://www.ferba.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product', 'sale', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/default.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}