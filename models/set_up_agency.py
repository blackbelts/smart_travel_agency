from datetime import timedelta, datetime
import base64
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import api, fields, models


class RatingTable(models.Model):
    _name = 'rating.table'
    _description = 'Set up Rating tables'


    geographical_coverage = fields.Selection([('all_countries', 'WorldWide + USA&CANADA'),
                                              ('not_all_countries', 'WorldWide - USA&CANADA'), ],
                                             'Geographical Coverage', required=True,
                                             default='not_all_countries')
    traveler_age = fields.Float('Traveler Age')
    coverage_period = fields.Float('Coverage Period')
    net_premium = fields.Float('Net Premium')
    proportional_stamp = fields.Float('Proportional Stamp')
    dimensional_stamp = fields.Float('Dimensional Stamp')
    supervisory_stamp = fields.Float('Supervisory Stamp')
    issue_fees = fields.Float('Issue Fees')
    gross_premium = fields.Float('Gross Premium')


class TravelAgency(models.Model):
    _name = 'travel.agency'
    _description = 'Set up Your Travel Agency'
    _rec_name = 'name'

    contract_from=fields.Date(string='Contract From',default=lambda self:fields.datetime.today())
    contract_to=fields.Date(string='Contract To',default=lambda self:fields.datetime.today())

    name = fields.Char('Agency Name', required=True)
    address = fields.Char('Address')
    email = fields.Char('Email')
    web_site = fields.Char('Website')

    contact_name = fields.Char('Contact Name')

    contact_number = fields.Char('Contact Mobile')
    contract_source = fields.Selection([('Broker', 'Broker'),
                               ('Direct', 'Direct'),
                               ],string='Contract Source',default='Direct')
    broker_name=fields.Char('Broker Name')
    broker_code= fields.Char('Broker Code')

    broker_code_expiration = fields.Date('Broker Code From')
    broker_valid_from = fields.Date('Broker Valid From')
    broker_valid_to = fields.Date('Broker Valid To')
    attachment = fields.Many2many('ir.attachment')
    agency_code = fields.Char('Agency Code',default=lambda self: self.env['ir.sequence'].next_by_code('agn'),)
    phone = fields.Char('Phone Number')
    mobile = fields.Char('Mobile Number')
    outstanding=fields.Float(string='Total OutStanding',)
    remain_outst=fields.Float(string='OutStanding')
    active = fields.Boolean(string="Active", default=True)
    max_outst=fields.Float('Max Outstanding')
    user=fields.Boolean()
    agency_comm=fields.One2many('travel.commission','travel_agency',string='Commission')
    branch_ids=fields.One2many('agency.branch','travel_agency',string='Branches')
    target_bonus_ids=fields.One2many('target.bonus','agency_id',string='Bonus Target')
    settle_ids=fields.One2many('agency.settle','agency_id',string='Settlements')
    @api.onchange('settle_ids')
    def _get_outstnding(self):
      total=0
      if self.settle_ids:
          for rec in self.settle_ids:
              total+=rec.amount
          self.outstanding-=total
    # @api.multi
    def create_agency_user(self):
            form = self.env.ref('smart_travel_agency.agents_user_wizard')
            self.user=True

            return {
                'name': ('Users'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'agent.user.wizard',
                # 'view_id': [(self.env.ref('smart_claim.tree_insurance_claim').id), 'tree'],
                'views': [(form.id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',

                'context': {'default_name': self.name,
                            'default_username': self.name,'default_travel_agency':self.id}

            }



class AgencyBranch(models.Model):
    _name = 'agency.branch'
    _description = 'Set up Your Travel Agency Branch'
    _rec_name = 'name'
    users=fields.One2many('res.users','travel_agency_branch',)
    name = fields.Char('Branch Name', required=True)
    travel_agency = fields.Many2one('travel.agency', 'Travel Agency',required=True)
    address = fields.Char('Address')
    email = fields.Char('Email')
    phone = fields.Char('Phone Number')
    mobile = fields.Char('Mobile Number')

    # @api.multi
    def create_branch_user(self):
        form = self.env.ref('smart_travel_agency.agents_user_wizard')
        self.user = True

        return {
            'name': ('Users'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'agent.user.wizard',
            # 'view_id': [(self.env.ref('smart_claim.tree_insurance_claim').id), 'tree'],
            'views': [(form.id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',

            'context': {'default_branch': True,'default_travel_agency_branch':self.id,'default_travel_agency':self.travel_agency.id}

        }




class CertificateBooklet(models.Model):
    _name = 'certificate.booklet'
    _description = 'Set up Your Certificate Booklet'

    booklet_num = fields.Char('Booklet Number', required=True)
    travel_agency = fields.Many2one('travel.agency', 'Travel Agency',required=True)
    travel_agency_branch = fields.Many2one('agency.branch', 'Agency Branch',
                                           domain="[('travel_agency','=',travel_agency)]",required=True,ondelete='cascade')
    serial_from = fields.Integer('Serial From')
    serial_to = fields.Integer('Serial To')


class Users(models.Model):
    _inherit = 'res.users'

    travel_agency = fields.Many2one('travel.agency', 'Travel Agency')
    travel_agency_branch = fields.Many2one('agency.branch', 'Agency Branch')

    address = fields.Char('Address')
    phone = fields.Char('Phone Number')
    mobile = fields.Char('Mobile Number')


class TravelAgencyCommission(models.Model):
    _name = 'travel.commission'
    _description = 'Set up Your Travel Commissions'

    travel_agency = fields.Many2one('travel.agency', 'Travel Agency')
    valid_from = fields.Date('Valid From', default=lambda self:fields.datetime.today())
    valid_to = fields.Date('Valid To', default=lambda self:fields.datetime.today())
    commission = fields.Float('Commission Rate')

class TravelAgencyTarget(models.Model):
    _name = 'target.bonus'
    _description = 'Set up Your Travel bonus'

    agency_id = fields.Many2one('travel.agency', 'Travel Agency',)
    bonus_from = fields.Date('From', default=lambda self:fields.datetime.today())
    bonus_to = fields.Date('To', default=lambda self:fields.datetime.today())
    target_count = fields.Float('Current Target')
    target_ach = fields.Boolean('Achieved',default=False)
    up_target = fields.Float('Above Target')
    bonus = fields.Float('bonus')
    @api.onchange('target_count','up_target')
    def get_target_achieved(self):
        if self.target_count:
            if self.target_count > self.up_target:
                self.target_ach=True



class TravelAgencySettlement(models.Model):
    _name = 'agency.settle'
    _description = 'Settlement'

    agency_id = fields.Many2one('travel.agency', 'Travel Agency',default=lambda self: self.env.user.travel_agency_branch.travel_agency.id)
    settle_date = fields.Date('Settlement Date', default=lambda self:fields.datetime.today())
    amount = fields.Float('Settlement Amount')
    attachment = fields.Many2many('ir.attachment',string='Your Files')


class GroupDiscount(models.Model):
        _name = 'group.discount'
        _description = 'Set up Your Travel Commissions'
        _rec_name = ''
        from_date=fields.Date('From Date')
        to_date=fields.Date('To Date')
        from_size = fields.Float('From Size')
        to_size = fields.Float('To Size')
        perc = fields.Float('Discount')


class NotUsedSerials(models.Model):
    _name = 'serial.available'
    _description = 'Get The not used Serial Numbers'

    travel_agency = fields.Many2one('travel.agency', 'Travel Agency', required=True)
    travel_agency_branch = fields.Many2one('agency.branch', 'Agency Branch',
                                           domain="[('travel_agency','=',travel_agency)]", required=True)
    numbers = fields.Char('Serial Numbers Not Used', readonly=True)

    # @api.multi
    def get_not_used_serial(self):
        serial = self.env['certificate.booklet'].search(
            [('travel_agency_branch', '=', self.travel_agency_branch.id)])

        records = []
        for rec in serial:
            print(111111)
            deff = rec.serial_to - rec.serial_from
            print(deff)
            x = 0
            for y in range(deff + 1):
                ser = rec.serial_from + x
                policy = self.env['policy.travel'].search(
                    [('state', '=', 'approved'), ('serial_no', '=', ser)])
                if not policy:
                    records.append(ser)
                y += 1
                x += 1
        print(records)
        self.numbers = records
        return {
            "type": "ir.actions.do_nothing",
        }

