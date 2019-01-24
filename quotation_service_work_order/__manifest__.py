# -*- coding: utf-8 -*-
# Part of BiztechCS. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quotation Based Service Workorder',
    'author': 'AppJetty',
    'version': '11.0.1.0.0',
    'summary': 'Workorders will be generated based on the unique equipment from the sale order.',
    'description': 'Service',
    'category': 'Sales & Service Work orders',
    'website': 'https://www.biztechconsultancy.com/',
    'depends': ['sale','biztech_service','mail','website_quote','general_template','account'],
    'data': [
             "views/quotation_service_workorder_view.xml",
             'views/account_dashboard_inherit.xml',
             'views/account_service_invoice_view.xml',
             'views/res_partner_mail.xml',
             'views/website_template.xml',
             'views/product_label_barcode_report.xml',
        ],
    'installable': True,
    'auto_install': False,
}


