# -*- coding: utf-8 -*-
# Part of BiztechCS. See LICENSE file for full copyright and licensing details.

{
    'name': 'Fleet Service Inventory',
    'author': 'AppJetty',
    'version': '11.0.1.0.0',
    'description': 'service work order integration with fleet',
    'category': 'Fleet and Inventory',
    'website': 'https://www.biztechconsultancy.com/',
    'depends': ['fleet','biztech_service','web'],
    'data': [
        'wizard/default_product_view.xml',
        'views/fleet_inventory_view.xml',
        'views/website_template.xml',
        'views/fleet_service_workorder_view.xml',
        'views/fleet_default_load_view.xml',
        'security/ir.model.access.csv',
        'views/fleet_menu_rearrange_service.xml',
        'views/initial_qty_quant_view.xml'
        ],
    'installable': True,
    'auto_install': False,
}


