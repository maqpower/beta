# -*- coding: utf-8 -*-
# Part of Biztech Consultancy. See LICENSE file for full copyright and licensing details.

{
    'name': 'Biztech Service Agreement Report',
    'version': '11.0.1.0.0',
    'author': 'BiztechCS',
    'description': ''' Biztech Service Agreement Report For Customers ''',

    'depends': ['sale'],
    'website': 'https://www.biztechconsultancy.com/',
    'data': [
        'security/ir.model.access.csv',
        'views/report_template.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
