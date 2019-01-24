# -*- coding: utf-8 -*-
# Part of Biztech Consultancy. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class CustomResPartner(models.Model):
    _inherit = 'res.partner'

    credit_check_verified = fields.Selection([
        ('no', 'NO'),
        ('yes', 'YES'),],string="Credit Check Verified", default='no')
    credit_rating = fields.Selection([
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        ('f', 'F')
    ], string="Credit Rating",)