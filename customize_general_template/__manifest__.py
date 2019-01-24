# -*- coding: utf-8 -*-
# Part of Biztech Consultancy. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom Customization of Clever all in one Reports',
    'version': '11.0.1.0.0',
    'description': """
   Add new template ('Classic') for SO,PO and Invoice.
    """,
    'author': 'BiztechCS',
    'depends': ['general_template','customize_product_list_view','biztech_service'],
    'website': 'http://www.biztechconsultancy.com',
    'data': [
        'views/sales_view.xml',
        'views/classic_sale.xml',
        'views/classic_purchase.xml',
        'views/classic_invoice.xml',
        'views/classic_quatation.xml',
        'views/classic_invoice_without_payment.xml',
        'views/classic_delivery.xml',
        'views/product_list_view_extended.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
