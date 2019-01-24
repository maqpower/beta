# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

{
    'name': 'Confirm Lead Quotation order',
    'author': 'AppJetty',
    'version': '11.0.1.0.0',
    'summary': 'Sale order diractly confirms when it created from CRM Lead.',
    'description': 'Service',
    'category': 'Sales orders',
    'website': 'https://www.biztechcs.com/',
    'depends': ['sale_crm'],
    'data': [
             "views/inherit_lead_to_opportunity_view.xml"
        ],
    'installable': True,
    'auto_install': False,
}


