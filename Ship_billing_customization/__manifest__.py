# -*- coding: utf-8 -*-
{
    'name': "Ship_billing_customization",
    'summary': """
        Ship Billing Drop view Customization. 
        """,
    'description': """
        Ship Billing Drop view Customization which is helpful to select the shipment details etc.
    """,
    'author': "Appjetty",
    'website': "https://www.appjetty.com/",
    'version': '11.0.1.0.0',
    'depends': ['sale','purchase','delivery','product','delivery_fedex'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order.xml',
    ],
}
