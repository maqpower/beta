# -*- coding: utf-8 -*-
# Part of Biztech Consultancy. See LICENSE file for full copyright and licensing details.
 
{
    'name': 'Product List View Modification',
    'version': '11.0.1.0.0',
    'description': """
   Customization Product list views.
    """,
    'author': 'BiztechCS',
    'depends': ['stock','website_sale'],
    'website': 'http://www.biztechconsultancy.com',
    'data': [
        'views/view.xml',
        'views/cron.xml',
    ],
    'installable': True,
    'auto_install': False,
}
