from odoo import models, tools, fields, api

class TravelExcess(models.Model):

    _name = 'travel.excess'
    rule = fields.Char(string="Rule")
    ar_rule = fields.Char(string="Arabic Rule")
    amount = fields.Char('Amount')