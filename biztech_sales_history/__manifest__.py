# -*- coding: utf-8 -*-
# Part of Biztech Consultancy. See LICENSE file for full copyright and licensing details.

{
    'name': 'Customer Sales History',
    'version': '11.0.1.0.0',
    'author': 'BiztechCS',
    'description': '''This module use for view history of 
            customer for his related sales ''',

    'depends': ['mail_push'],
    'website': 'https://www.biztechconsultancy.com/',
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/customer_sale_history_menu.xml'
    ],
    'installable': True,
    'auto_install': False,
}
