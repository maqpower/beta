# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def default_get(self, default_fields):
        res = super(ResPartner, self).default_get(default_fields)
        res.update({
            'company_type': 'company',
            'is_company': True
            })
        return res
