from odoo import models, tools, fields, api

class TravelBenefits(models.Model):
    _name = 'travel.benefits'
    cover = fields.Char(string="Cover")
    ar_cover = fields.Char(string="Arabic Cover")
    limit = fields.Char('Limit (USD)')
    ar_limit = fields.Char('Arabic Limit (USD)')
    special_covers = fields.Boolean('Special Covers')