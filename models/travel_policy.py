from datetime import timedelta, datetime
import base64
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import api, fields, models,exceptions
import  math

class TravelPolicy(models.Model):
    _name = 'policy.travel'
    _description = 'Create Your Travel Policies'
    _rec_name = 'policy_num'

    # @api.multi
    @api.model
    def send_mail_template(self,mail):

        # mail='eslam3bady@gmail.com'
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = self.env.ref('smart_travel_agency.email_template')
        template_id.write({'email_to': mail})

        template_id.send_mail(self.ids[0], force_send=True)
        # self.env['mail.template'].browse(template_id.id).send_mail(self.id)

    package = fields.Selection([('individual', 'Individual'), ('family', 'Family')], 'Package For', default='individual')

    policy_num = fields.Char(string='Policy Number', required=True, copy=False, index=True,
                             default=lambda self: self.env['ir.sequence'].next_by_code('policy'), readonly=True)
    state = fields.Selection([('pending', 'Pending'),
                              ('approved', 'Approved'),
                              ('canceled', 'Canceled'), ],
                             'Status', required=True, default='pending', copy=False)
    type = fields.Selection([('issue', 'Issue'), ('cancel', 'Cancel')], readonly=True, default='issue')
    issue_date = fields.Datetime(string='Issue Date', readonly=True, default=lambda self:fields.datetime.today())
    serial_no = fields.Integer('Serial Number')
    insured = fields.Char('Traveller Name')
    phone = fields.Char('Traveller Phone')

    address = fields.Char('Traveller Address')
    passport_num = fields.Char('Passport Number')
    expiry_date = fields.Date(' Expiration Date')
    national_id = fields.Char('National ID')
    source = fields.Selection([('online', 'Online'),
                               ('Agency', 'Agency'),
                               ], default='Agency')
    DOB = fields.Date('Date Of Birth', default=datetime.today())
    age = fields.Integer('Age', compute='compute_age',store=True)
    gender = fields.Selection([('M', 'Male'), ('F', 'Female')])
    trip_from = fields.Many2one('res.country', 'Trip From')
    trip_to = fields.Many2one('res.country', 'Trip To')
    coverage_from = fields.Date('From', default=datetime.today())
    coverage_to = fields.Date('To')
    days = fields.Integer('Day(s)',compute='compute_days',store='True')
    geographical_coverage = fields.Selection([('zone 1', 'Europe'),
                                              ('zone 2', 'Worldwide excluding USA & CANADA'),
                                              ('zone 3', 'Worldwide'), ],
                                             'Zone',
                                             default='zone 1')

    currency_id = fields.Many2one("res.currency", "Currency", copy=True,
                                  default=lambda self: self.env.user.company_id.currency_id, readonly=True)
    net_premium = fields.Float('Net Premium', readonly=True, compute='get_financial_data',store=True)
    proportional_stamp = fields.Float('Proportional Stamp', readonly=True, compute='get_financial_data' ,store=True)
    dimensional_stamp = fields.Float('Dimensional Stamp', readonly=True, compute='get_financial_data',store=True)
    supervisory_stamp = fields.Float('Supervisory Stamp', readonly=True, compute='get_financial_data',store=True)
    policy_approval_fees = fields.Float('Policy approval fees', readonly=True, compute='get_financial_data', store=True)
    policy_holder_fees = fields.Float('Policyholder’s protection fees', readonly=True, compute='get_financial_data', store=True)
    admin_fees = fields.Float('Admin Fees', )

    issue_fees = fields.Float('Issue Fees', readonly=True, compute='get_financial_data',store=True)
    gross_premium = fields.Float('Gross Premium', readonly=True, compute='get_financial_data',store=True)
    travel_agency = fields.Many2one('travel.agency', 'Travel Agency', related='travel_agency_branch.travel_agency',store=True
                                    )
    travel_agency_branch = fields.Many2one('agency.branch', 'Agency Branch',
                                           domain="[('travel_agency','=',travel_agency)]",
                                           related='user_id.travel_agency_branch', readonly=True)
    user_id = fields.Many2one('res.users', 'User Name', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user, readonly=True)
    duration=fields.Selection('_get_periods',string='Duration',store=True)
    cancel_reason = fields.Char('Cancel Reason')
    travel_agency_comm = fields.Float('Agency Commission',compute='get_financial_data',store=True)
    agent_commission=fields.Float('commission',compute='get_financial_data',store=True)
    bonus_commission=fields.Float('Bonus Commission',compute='get_financial_data',store=True)

    net_to_insurer = fields.Float('Net To Insurer', compute='get_financial_data',store=True)
    is_canceled = fields.Boolean(default=False)
    family_age = fields.One2many('policy.family.age','policy_id', ondelete='cascade', string='Family Age')
    price_details = fields.Boolean('Show Price Details In Policy', default=False)

    def test(self):
        self.send_mail_template('AhmedNourElhalaby@gmail.com')
        
    def _get_periods(self):
        options = []
        data = self.env['travel.price.line'].search(
            [('price_id.package', '=', 'individual'), ('price_id.zone', '=', 'zone 1'),
             ('price_id.from_age', '=', 0.00)],)
        for option in data:
            options.append((str(option.period),str(option.period)+' Days'))
        print(options)
        return options
    # @api.onchange('admin_fees','gross_premium')
    # def get_new_gross(self):
    #     if self.admin_fees :
    #         self.gross_premium=self.gross_premium+self.admin_fees
    # @api.one
    @api.depends('coverage_from', 'coverage_to')
    def compute_days(self):
        if self.coverage_from and self.coverage_to:
            # date1 = datetime.strptime(self.coverage_from, '%Y-%m-%d').date()
            # date2 = datetime.strptime(self.coverage_to, '%Y-%m-%d').date()
            date3 = (self.coverage_to - self.coverage_from).days
            self.days = date3

    # @api.one
    def unlink(self):
        if self.state != ('pending'):
            raise UserError((
                'You cannot delete an Approved Policy'))
        return super(TravelPolicy, self).unlink()

    # @api.one
    @api.depends('DOB')
    def compute_age(self):
        if self.DOB:
            # date1 = datetime.strptime(str(self.issue_date), '%Y-%m-%d %H:%M:%S').date()
            # date2 = datetime.strptime(str(self.DOB), '%Y-%m-%d' ).date()
            difference = relativedelta(self.issue_date, self.DOB)
            age = difference.years
            months = difference.months
            days = difference.days
            if months or days != 0:
                age += 1
            self.age = age



    @api.onchange('coverage_from','duration')
    def get_end_date(self):
        if self.coverage_from and self.duration:
            self.coverage_to=self.coverage_from+timedelta(days=int(self.duration))

    # @api.depends('age', 'geographical_coverage', 'days')
    # @api.one
    def get_bonus_data(self):
        if self.travel_agency:
            bonus = self.env['target.bonus'].search(
                [('agency_id', '=', self.travel_agency.id), ('bonus_from', '<=', self.issue_date),
                 ('bonus_to', '>=', self.issue_date), ('target_ach', '=', True)], limit=1)
            for record in bonus:
                self.bonus_commission = (record.bonus / 100) * self.net_premium

    # @api.one
    # @api.model
    def get_financial_data(self):
        if self.age and self.geographical_coverage and self.days:
            # data = self.env['travel.price'].search(
            #     [('zone', '=', self.geographical_coverage)])
            result={}
            kid_dob=[]
            if self.days>0 :
                for rec in self.family_age:
                    if rec.type=='kid':
                       kid_dob.append(rec.DOB)
                # print(kid_dob)

                if self.package == 'individual':
                    result=self.get_individual({'z':self.geographical_coverage,'d':[self.DOB],'p_from':self.coverage_from,'p_to':self.coverage_to})


                elif self.package == 'family':
                    result=self.get_family({'z':self.geographical_coverage,'p_from':self.coverage_from,'p_to':self.coverage_to,'kid_dob':kid_dob})
                    # result=self.get_group({'zone':self.geographical_coverage,'p_from':self.coverage_from,'p_to':self.coverage_to,'group':[{'size':20,'age':5},{'size':50,'age':20}]})
                print(result)
                if result:
                    self.net_premium =  result.get('net')
                    self.proportional_stamp = result.get('pro_stamp')
                    self.dimensional_stamp = result.get('dimensional_stamp')
                    self.supervisory_stamp = result.get('supervisory_stamp')
                    self.policy_approval_fees = result.get('policy_approval_fees')
                    self.policy_holder_fees = result.get('policy_holder_fees')
                    self.issue_fees = result.get('issue_fees')
                    self.gross_premium = result.get('gross')+self.admin_fees
                if self.travel_agency:
                    print('kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
                    comm = self.env['travel.commission'].search([('travel_agency', '=', self.travel_agency.id)],limit=1)

                    print('kkkkkkkkkkkkkkkkkkkkkkkkkkkk')
                    for rec in comm:
                            print(rec.commission)
                            self.travel_agency_comm = (rec.commission / 100)
                            self.agent_commission = self.net_premium * self.travel_agency_comm
                self.net_to_insurer = self.gross_premium - self.agent_commission
            else:
                raise UserError((
                    "Period Is Incorrect Or Age Is Incorrect "))



    @api.model
    def get_individual(self,data):
        if data.get('z') and data.get('d') and data.get('p_from') and data.get('p_to'):
            result = {}


            geographical_coverage=data.get('z')
            DOB=data.get('d')
            coverage_from=data.get('p_from')
            coverage_to=data.get('p_to')

            # dob=[DOB]
            days=self.calculate_period(coverage_from,coverage_to)
            age=self.calculate_age(DOB)

            data = self.env['travel.price'].search(
                [('zone', '=', geographical_coverage),('from_age','<=',age[0]),('to_age','>=',age[0])])

            opj = []
            for rec in data.price_lines:
                if days <= rec.period:
                    opj.append(rec.period)
            if opj:
                    min_period = min(opj)
                    print(min_period)
                    for record in data:
                        for rec in record.price_lines:
                          if rec.period == min_period:
                                    result['net'] = rec.net_premium*(record.currency_id.rate)
                                    result['pro_stamp'] = rec.proportional_stamp *(record.currency_id.rate)
                                    result['dimensional_stamp'] = rec.dimensional_stamp *(record.currency_id.rate)
                                    result['supervisory_stamp'] = rec.supervisory_stamp *(record.currency_id.rate)
                                    # self.issue_fees = record.issue_fees
                                    fra,result['gross'] = math.modf(rec.gross_premium *(record.currency_id.rate))
                                    result['issue_fees'] = (rec.issue_fees *(record.currency_id.rate))+(1-fra)

                                    print("fraction")
                                    print (fra)

            return result

    @api.model
    def get_family(self,data):
        if data.get('z') and data.get('p_from') and data.get('p_to'):
            geographical_coverage = data.get('z')
            coverage_from = data.get('p_from')
            coverage_to = data.get('p_to')
            days=self.calculate_period(coverage_from,coverage_to)
            res = {}
            final_kid=[]
            for rec in data.get('kid_dob'):
                age = self.calculate_age([rec])
                if 15<=age[0]<=18:
                    # print(zone)
                    # print(period_from)
                    # print(period_to)
                    print ([rec])
                    res=self.get_individual({'z':geographical_coverage,'d':[rec],'p_from':coverage_from,'p_to':coverage_to})
                    final_kid.append(res)
                    print('8888888888888888888888888888888888888888888888888888888888888888888888')
                print(res)

                print ('eslammmmmmmmmmmmmmmmmmmmmmmmmmmmmmm99999999999999')
                print(age[0])
            result = {}
            data = self.env['travel.price'].search(
                [('zone', '=',geographical_coverage),('package','=','family')])

            opj = []
            for rec in data.price_lines:
                if days <= rec.period:
                    opj.append(rec.period)
            if opj:
                    min_period = min(opj)
                    for rec in data:
                     for record in rec.price_lines:
                        if record.period == min_period:
                            result['net'] = record.net_premium *(rec.currency_id.rate)
                            result['pro_stamp'] = record.proportional_stamp *(rec.currency_id.rate)
                            result['dimensional_stamp'] = record.dimensional_stamp *(rec.currency_id.rate)
                            result['supervisory_stamp'] = record.supervisory_stamp*(rec.currency_id.rate)
                            # self.issue_fees = record.issue_fees
                            fra,result['gross'] = math.modf(record.gross_premium *(rec.currency_id.rate))
                            result['issue_fees'] = (record.issue_fees * (rec.currency_id.rate)) + (1 - fra)

                            print("fraction")
                            print(fra)
                    print(result)
            if final_kid:
               for record in final_kid:
                   result['net'] = (record.get('net') *.5)+result.get('net')
                   result['pro_stamp'] = (record.get('pro_stamp') *.5)+result.get('pro_stamp')
                   result['supervisory_stamp'] = (record.get('supervisory_stamp') *.5)+result.get('supervisory_stamp')
                   result['issue_fees'] = (record.get('issue_fees') *.5)+result.get('issue_fees')
                   result['gross'] = (record.get('gross') *.5)+result.get('gross')
                   print(fra)
                   print('kid')
                   print(record)
                   print('final')

            return result

    @api.model
    def get_group(self,data):
        if data.get('zone') and data.get('p_from') and data.get('p_to'):
            days=self.calculate_period(data.get('p_from'),data.get('p_to'))
            result={'net':0.0,'pro_stamp':0.0,'dimensional_stamp':0.0,'supervisory_stamp':0.0,'gross':0.0,'issue_fees':0.0}
            discount=0.0
            for group in data.get('group'):
               price_discount=self.env['group.discount'].search(
                  [('from_date','<=',datetime.today()),('to_date','>=',datetime.today()),('from_size', '<=',group['size']), ('to_size', '>=', group['size'])])
               if price_discount:
                   discount=price_discount.perc

               price = self.env['travel.price'].search(
                  [('zone', '=', data.get('zone')), ('from_age', '<=',group['age']), ('to_age', '>=', group['age'])])

               opj = []
               for rec in price.price_lines:
                   if days <= rec.period:
                       opj.append(rec.period)
               if opj:
                   min_period = min(opj)
                   print(min_period)
                   for record in price:
                       for rec in record.price_lines:
                           if rec.period == min_period:
                                   result['net'] +=rec.net_premium * record.currency_id.rate*group.get('size')*(1-(discount/100))
                                   result['pro_stamp'] += rec.proportional_stamp * (record.currency_id.rate)*group.get('size')*(1-(discount/100))
                                   result['dimensional_stamp'] += rec.dimensional_stamp * (record.currency_id.rate)*group.get('size')*(1-(discount/100))
                                   result['supervisory_stamp'] += rec.supervisory_stamp * (record.currency_id.rate)*group.get('size')*(1-(discount/100))
                                   result['issue_fees'] += rec.issue_fees * (record.currency_id.rate)*group.get('size')*(1-(discount/100))

                                   # self.issue_fees = record.issue_fees
                                   result['gross'] += rec.gross_premium * (record.currency_id.rate)*group.get('size')*(1-(discount/100))

            return result



    @api.model
    def calculate_age(self, DOB):
        ages = []
        for rec in DOB:
            today = datetime.today().date()
            if isinstance(rec, str) == True:
                DOB = datetime.strptime(rec, '%Y-%m-%d').date()
                difference = relativedelta(today, DOB)
            else:
                difference = relativedelta(today, rec)
            age = difference.years
            months = difference.months
            days = difference.days
            if months or days != 0:
                age += 1
            ages.append(age)
        return ages

    @api.model
    def calculate_period(self,when,to):
        if isinstance(when, str) == True:
            when = datetime.strptime(when, '%Y-%m-%d').date()
        if isinstance(to, str) == True:
            to = datetime.strptime(to, '%Y-%m-%d').date()
        period = (to - when).days
        return period

    @api.model
    @api.constrains('coverage_from')
    def _check_date(self):
        if self.coverage_from:
            # date1 = datetime.strptime(self.issue_date, '%Y-%m-%d %H:%M:%S').date()
            # date2 = datetime.strptime(self.coverage_from, '%Y-%m-%d').date()
            difference = relativedelta(self.coverage_from, self.issue_date.date())
            if difference.days <=0:
                raise exceptions.ValidationError('Coverage Date Must Be After The Issuing')


    def _check_agency_limit(self,net):
        if self.travel_agency:
            if net+self.travel_agency.outstanding > self.travel_agency.max_outst:
                raise exceptions.ValidationError('You Exceed The Max Outstanding Limit Please Make A Settlement')

    @api.constrains('age')
    def _check_age_limit(self):
        if self.age <= 0:
                raise exceptions.ValidationError('You Must Enter Correct Birth Date')


    # @api.multi
    def confirm_policy(self):
        if self.address and self.insured and self.passport_num and self.DOB and self.gender and self.geographical_coverage and self.days:
            self.get_financial_data()
            self.state = 'approved'
            self.travel_agency.outstanding+=self.net_to_insurer
            bonus = self.env['target.bonus'].search(
                [('agency_id', '=', self.travel_agency.id), ('bonus_from', '<=', self.issue_date),
                 ('bonus_to', '>=', self.issue_date)], limit=1)
            if bonus:
                bonus.target_count+=self.gross_premium
                bonus.get_target_achieved()
            self.get_bonus_data()
            self._check_agency_limit(self.net_to_insurer)


            # serial = self.env['certificate.booklet'].search(
            #     [('travel_agency_branch', '=', self.travel_agency_branch.id)])
            # print(serial)
            # serial2 = self.env['policy.travel'].search(
            #     [('serial_no', '=', self.serial_no), ('id', '!=', self.id)])
            # print(serial2)
            # records = []
            # if serial2:
            #     raise UserError((
            #         "Document Serial Number already exists!"))
            # else:
            #     for rec in serial:
            #         deff = rec.serial_to - rec.serial_from
            #         print(deff)
            #         x = 0
            #         for y in range(deff + 1):
            #             print(11111111111)
            #             ser = rec.serial_from + x
            #             records.append(ser)
            #             y += 1
            #             x += 1
            #     print(records)
            #     if self.serial_no in records:
            #         print(6666666666666)
            #         self.state = 'approved'
            #         # break
            #     else:
            #         raise UserError((
            #             "Your Serial Number doesn't match your Branch Serial Numbers "))
        else:
            raise UserError((
                "You Must Enter All The Policy Data"))

    # @api.multi
    def get_benefits(self):
        return self.env['travel.benefits'].search([])

    # @api.multi
    def get_assistance_information(self):
        return self.env['travel.company.assist'].search([])




class NewModule(models.Model):
    _name = 'cancel.policy'

    cancel_reason = fields.Char('Your Cancel Reason')

    # @api.multi
    def cancel_policy(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        if self.cancel_reason:
            for rec in self.env['policy.travel'].search([('id', 'in', active_ids)]):
                if  rec.state == 'approved':
                    rec.create(
                        {'state': 'canceled', 'policy_num': rec.policy_num, 'issue_date': rec.issue_date,
                         'type': 'cancel',
                         'insured': rec.insured, 'address': rec.address, 'serial_no': rec.serial_no,
                         'passport_num': rec.passport_num, 'DOB': rec.DOB, 'age': rec.age, 'gender': rec.gender,
                         'coverage_from': rec.coverage_from,
                         'geographical_coverage': rec.geographical_coverage, 'coverage_to': rec.coverage_to,
                         'days': rec.days, 'currency_id': rec.currency_id.id, 'net_premium': (rec.net_premium*-1) ,
                         'proportional_stamp': (rec.proportional_stamp* -1), 'issue_fees': (rec.issue_fees*-1),
                         'dimensional_stamp': (rec.dimensional_stamp*-1), 'gross_premium': (rec.gross_premium*-1),
                         'supervisory_stamp': (rec.supervisory_stamp*-1), 'travel_agency': rec.travel_agency.id,
                         'travel_agency_branch': rec.travel_agency_branch.id, 'user_id': rec.user_id.id,
                         'travel_agency_comm': (rec.travel_agency_comm*-1), 'net_to_insurer': (rec.net_to_insurer * -1),
                         'cancel_reason': self.cancel_reason,
                         'is_editable': False, 'is_canceled': True})
                    rec.write({'is_canceled': True})
                else:
                    raise UserError((
                        'This Policy is Approved or Canceled!'))

        else:
            raise UserError((
                'You have to insert your Cancel Reason !'))

        return {'type': 'ir.actions.act_window_close'}


class FamilyAge(models.Model):
    _name = 'policy.family.age'


    issue_date = fields.Datetime(string='Issue Date', default=lambda self:fields.datetime.today())
    name=fields.Char('name',required=True)
    type=fields.Selection([('spouse', 'Spouse'),
                           ('kid', 'kid'),
                           ('brother','brother'),
                           ('sister','sister'),
                           ('parent', 'parent'),
                           ('grandparents', 'grandparents'),
                           ],default='spouse')

    gender = fields.Selection([('M', 'Male'), ('F', 'Female')])
    age=fields.Float('age')
    DOB = fields.Date('Date Of Birth',required=True)
    pass_num = fields.Char('Passport',required=True)
    # @api.one
    @api.constrains('age')
    def _check_age(self):
        if self.age:
            if self.age>18 and self.type=='kid':
                raise exceptions.ValidationError('Kid Age Must  Be  Less Than 18')
    policy_id = fields.Many2one('policy.travel', ondelete='cascade')
    @api.model
    @api.onchange('DOB')
    def get_age(self):
        if self.DOB:
            # date1 = datetime.strptime(self.issue_date, '%Y-%m-%d %H:%M:%S').date()
            # date2 = datetime.strptime(self.DOB, '%Y-%m-%d').date()
            difference = relativedelta(self.issue_date, self.DOB)
            age = difference.years
            months = difference.months
            days = difference.days
            if months or days != 0:
                age += 1
            self.age = age

class TravelCompanyAssist(models.Model):
    _name = 'travel.company.assist'

    company_name = fields.Char('Company Name')
    hot_line = fields.Char('Hotline')
    whats_app = fields.Char('WhatsApp')
    spain = fields.Char('Spain')
    fax = fields.Char('Fax')
    mobile_app = fields.Char('Mobile App')
    email = fields.Char('Email')
    fb_messenger = fields.Char('FB Messenger')
    logo_url = fields.Char('Logo Url')