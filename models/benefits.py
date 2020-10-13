from odoo import models, tools, fields, api

class TravelBenefits(models.Model):
    _name = 'travel.benefits'
    cover = fields.Char(string="Cover")
    ar_cover = fields.Char(string="Arabic Cover")
    limit = fields.Char('Limit (USD)')
    ar_limit = fields.Char('Arabic Limit (USD)')
    special_covers = fields.Boolean('Special Covers')
    cover_rate = fields.Float('Cover Rate')
    active_online = fields.Boolean('Active Online')


class TravelAgencySettlement(models.Model):
    _name = 'agency.settle'
    _description = 'Settlement'

    agency_id = fields.Many2one('travel.agency', 'Travel Agency')
    settle_date = fields.Date('Settlement Date', default=lambda self:fields.datetime.today())
    amount = fields.Float('Settlement Amount')
    attachment = fields.Many2many('ir.attachment',string='Your Files')