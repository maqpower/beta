# -*- coding: utf-8 -*-
# Part of Biztech Consultancy. See LICENSE file for full copyright and licensing details.

{
    'name': 'Invoice Attachement & Vendor label',
    'version': '11.0.1.0.0',
    'description': """
   Find ths miss attachement in invoice.add lable for vandor account in internal notes.
    """,
    'author': 'BiztechCS',
    'depends': ['document', 'account'],
    'website': 'http://www.biztechconsultancy.com',
    'data': [
        'views/view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
