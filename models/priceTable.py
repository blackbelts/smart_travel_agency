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
    issue_fees = fields.Float('Issue Fees',compute='compute_fields',store=True)
    net_premium = fields.Float('Net Premium')
    proportional_stamp = fields.Float('Proportional Stamp', compute='compute_fields',store=True)
    policy_approval_fees = fields.Float('Policy approval fees',compute='compute_fields',store=True)
    policy_holder_fees = fields.Float('Policyholder’s protection fees',compute='compute_fields',store=True)
    dimensional_stamp = fields.Float('Dimensional Stamp')
    supervisory_stamp = fields.Float('Supervisory Stamp',compute='compute_fields',store=True)
    gross_premium = fields.Float('Gross Premium',compute='compute_fields',store=True)
    price_id=fields.Many2one('travel.price', ondelete='cascade')


    #you Must Delete Gross Prem or make it computed

    def compute_fields(self):
        if self.net_premium:
            self.proportional_stamp = round(self.net_premium*(.5/100),2)
            self.supervisory_stamp = round(self.net_premium * (.6 / 100), 2)
            self.policy_approval_fees = round(self.net_premium * (.1 / 100), 2)
            self.policy_holder_fees = round(self.net_premium * (.2 / 100), 2)
            x = self.issue_fees + self.net_premium + self.proportional_stamp + self.policy_approval_fees + \
                self.policy_holder_fees + self.dimensional_stamp + self.supervisory_stamp

            f = x - int(x)
            complement = 1 - f
            if complement == 1:
                self.issue_fees = self.issue_fees
            else:
                self.issue_fees = self.issue_fees + complement
            self.gross_premium = self.issue_fees + self.net_premium + self.proportional_stamp + self.policy_approval_fees + \
                self.policy_holder_fees + self.dimensional_stamp + self.supervisory_stamp


class InsuranceProducts(models.Model):
    _inherit = 'insurance.product'

    ar_product_name = fields.Char('Arabic Product Name')
    active_online = fields.Boolean('Active Online')