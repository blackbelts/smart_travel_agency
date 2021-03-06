from datetime import timedelta, datetime
import base64
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import api, fields, models

class HelpDesk(models.Model):
    _inherit = 'quoate'
    group=fields.One2many('group.ticket','group_id',string='Group')

class HelpGroup(models.Model):
        _name = 'group.ticket'
        range = fields.Char('Range')
        size = fields.Float('Size')
        group_id = fields.Many2one('helpdesk_lite.ticket', string='ticket')

class Travelapi(models.Model):
    _name='travel.front'

    # @api.multi
    def create_test(self):
        self.create_policy({'package':'family','dob':'2002-1-1','p_from':'2020-5-30','p_to':'2020-6-3','family':[{'name':'eslam','dob':'2005-12-2','passport_num':587961,'type':'kid','gender':'M'}]})

    @api.model
    def create_policy(self, data):
        DOB = datetime.strptime(data.get('dob'), '%Y-%m-%d').date()
        when = datetime.strptime(data.get('p_from'), '%Y-%m-%d').date()
        to = datetime.strptime(data.get('p_to'), '%Y-%m-%d').date()

        policy_id = self.env['policy.travel'].create(
            {'product': data.get('product'),'package': data.get('package'), 'insured': data.get('c_name'),
             'address': data.get('add'), 'f_name': data.get('s_name'), 's_name': data.get('f_name'), 'l_name': data.get('l_name'),
             'gender': data.get('gender'), 'source': data.get('source'), 'passport_num': data.get('pass'),
             'national_id': data.get('id'), 'phone': data.get('phone'),'country': data.get('destination'),
             'DOB': DOB, 'geographical_coverage': data.get('zone'), 'coverage_from': when, 'coverage_to': to,
             'state': 'approved',
             # 'special_beneifts':[(6,0,data['s_covers'])] if data['s_covers'] else False
             })
        if data.get('family'):
            for rec  in data.get('family'):
               f= self.env['policy.family.age'].create(
                    {'pass_num': rec['passport_num'], 'name': rec['name'], 'DOB': rec['dob'], 'type': rec['type'],
                     'gender': rec['gender'], 'policy_id': policy_id.id})

               self.env['policy.family.age'].search([('id', '=', f.id)]).get_age()

        self.env['policy.travel'].search([('id', '=', policy_id.id)]).get_financial_data()
        self.env['policy.travel'].search([('id', '=', policy_id.id)]).get_price_calculations()
        self.env['policy.travel'].search([('id', '=', policy_id.id)]).send_mail_template(data.get('mail'))
        return [policy_id.id,policy_id.policy_num]

    @api.model
    def get_periods(self,data):
        # You Must Change it very soon
        x = data
        options = []
        # data = self.env['travel.price.line'].search([('price_id.package', '=', 'individual'),
        #                                              ('price_id.zone', '=', 'zone 1'),
        #                                              ('price_id.from_age', '=', 0.00)])
        data = self.env['travel.price.line'].search([('price_id.product', '=', data.get('product'))])
        for option in data:
            if option.dispaly_period:
                options.append({'value':option.period, 'display': option.dispaly_period})
        seen = []
        for x in options:
            if x not in seen:
                seen.append(x)
        print(options)
        return seen

    @api.model
    def create_travel_ticket(self, data):
        name = 'Travel Group Ticket'
        group_dict = {5: '0-10', 15: '11-18', 25: '19-70'}
        support_team = self.env['helpdesk_lite.team'].search([('team_support_type', '=', 'travel')],limit=1).id
        ticket_id = self.env['quoate'].create(
            {'name': name, 'contact_name': data.get('name'), 'phone': data.get('phone'),
             'email_from': data.get('mail'), 'ticket_type':'travel', 'support_team': support_team,'source': 'online'})
        if data.get('group'):
            for rec in data.get('group'):
                self.env['group.ticket'].create(
                    {'size': rec['size'], 'range': group_dict.get(rec['age']), 'group_id': ticket_id.id})
        self.env['quoate'].search([('id', '=', ticket_id.id)]).onchange_support_team()
        return ticket_id.id

    @api.model
    def get_covers(self, data):
        covers = []
        if data.get('type') == 'individual':
            age = self.env['policy.travel'].calculate_age(data.get('d'))
            for rec in self.env['travel.price'].search([('product', '=', data.get('product_id')),
                                                        ('zone', '=', data.get('zone')),('from_age','<=',age[0]),('to_age','>=',age[0])]).covers:
                covers.append({'id': rec.id, 'cover': rec.cover, 'limit': rec.limit,
                               'ar_cover': rec.ar_cover, 'ar_limit': rec.ar_limit})
            return covers
        else:
            for rec in self.env['travel.price'].search([('product', '=', data.get('product_id')),
                                                        ('zone', '=', data.get('zone')), ('package', '=', 'family')]).covers:
                covers.append({'id': rec.id, 'cover': rec.cover, 'limit': rec.limit,
                               'ar_cover': rec.ar_cover, 'ar_limit': rec.ar_limit})
            return covers
