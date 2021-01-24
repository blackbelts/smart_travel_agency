from odoo import models, tools, fields, api

class PriceTable(models.Model):
    _name = 'travel.price'
    _description = 'Set up Price tables'
    product = fields.Many2one('insurance.product', string='Product', domain="[('line_of_bus.line_of_business', '=', 'Travel')]")

    package = fields.Selection([('individual', 'Individual'),
                             ('family', 'Family'),],
                            'Package For',
                            default='individual')

    zone = fields.Selection([('01', 'Europe'),
                                              ('02', 'Worldwide excluding USA & CANADA'),
                                              ('03', 'Worldwide'), ],
                                             'Zone',
                                             default='01')
    currency_id=fields.Many2one('res.currency')
    from_age = fields.Float('From Age')
    to_age = fields.Float('To Age')

    covers = fields.Many2many('travel.benefits', string='Covers')

    price_lines=fields.One2many('travel.price.line','price_id',string='Prices')

class PriceTable(models.Model):
    _name = 'travel.price.line'

    period = fields.Integer('Period')
    dispaly_period = fields.Char('Display Period')
    issue_fees = fields.Float('Issue Fees')
    net_premium = fields.Float('Net Premium')
    proportional_stamp = fields.Float('Proportional Stamp')
    policy_approval_fees = fields.Float('Policy approval fees ')
    policy_holder_fees = fields.Float('Policyholder’s protection fees ')
    dimensional_stamp = fields.Float('Dimensional Stamp')
    supervisory_stamp = fields.Float('Supervisory Stamp')
    gross_premium = fields.Float('Gross Premium')
    price_id=fields.Many2one('travel.price', ondelete='cascade')


    #you Must Delete Gross Prem or make it computed

    @api.onchange('net_premium','issue_fees', 'dimensional_stamp')
    @api.constrains('net_premium','issue_fees', 'dimensional_stamp')
    def compute_fields(self):
        for rec in self:
            if rec.net_premium:
                rec.proportional_stamp = round(rec.net_premium*(.5/100),2)
                rec.supervisory_stamp = round(rec.net_premium * (.6 / 100), 2)
                rec.policy_approval_fees = round(rec.net_premium * (.1 / 100), 2)
                rec.policy_holder_fees = round(rec.net_premium * (.2 / 100), 2)
                x = rec.issue_fees + rec.net_premium + rec.proportional_stamp + rec.policy_approval_fees + \
                    rec.policy_holder_fees + rec.dimensional_stamp + rec.supervisory_stamp

                f = x - int(x)
                complement = 1 - f
                if complement == 1:
                    rec.write({'issue_fees': rec.issue_fees})
                else:
                    rec.write({'issue_fees' : rec.issue_fees + complement})
                rec.gross_premium = rec.issue_fees + rec.net_premium + rec.proportional_stamp + rec.policy_approval_fees + \
                    rec.policy_holder_fees + rec.dimensional_stamp + rec.supervisory_stamp


class InsuranceProducts(models.Model):
    _inherit = 'insurance.product'

    ar_product_name = fields.Char('Arabic Product Name')
    active_online = fields.Boolean('Active Online')