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

    @api.model
    def create(self, vals):
        serial_no = self.env['ir.sequence'].next_by_code('policy')
        if self.env.user.has_group('smart_travel_agency.head_office_group'):
            vals['policy_num'] = 'THO' + str(serial_no)
            return super(TravelPolicy, self).create(vals)
        else:
            vals['policy_num'] = 'TAS' + str(serial_no)
            return super(TravelPolicy, self).create(vals)




    product = fields.Many2one('insurance.product', string='Product', domain="[('line_of_bus.line_of_business','=','Travel')]")
    package = fields.Selection([('individual', 'Individual'), ('family', 'Family')], 'Package For', default='individual')

    policy_num = fields.Char(string='Policy Number', required=True, copy=False, index=True,
                             default=lambda self: self.env['ir.sequence'].next_by_code('policy'), readonly=True)
    state = fields.Selection([('pending', 'Draft'),
                              ('approved', 'Issued'),
                              ('canceled', 'Canceled'), ],
                             'Status', required=True, default='pending', copy=False)
    # country = fields.Many2one('res.country', 'Destination')
    type = fields.Selection([('issue', 'Issue'), ('cancel', 'Cancel')], readonly=True, default='issue')
    issue_date = fields.Datetime(string='Issue Date', readonly=True, default=lambda self:fields.datetime.today())
    serial_no = fields.Integer('Serial Number')
    insured = fields.Char('Traveller Name')
    phone = fields.Char('Traveller Phone')
    order_id = fields.Many2one('orders', 'Order ID', readonly=True)

    address = fields.Char('Traveller Address')
    passport_num = fields.Char('Passport Number')
    expiry_date = fields.Date(' Expiration Date')
    national_id = fields.Char('National ID')
    source = fields.Selection([('online', 'Online'),
                               ('Agency', 'Agency'),
                               ], default='Agency')
    broker = fields.Many2one('persons', string="Broker" ,domain="[('type','=','broker')]")
    broker_agent_code = fields.Char(related='broker.agent_code', string="Broker code" )

    DOB = fields.Date('Date Of Birth', default=lambda self:fields.datetime.today())
    age = fields.Integer('Age', compute='compute_age',store=True)
    gender = fields.Selection([('M', 'Male'), ('F', 'Female')])
    trip_from = fields.Many2one('res.country', 'Trip From')
    trip_to = fields.Many2one('res.country', 'Trip To')
    coverage_from = fields.Date('From', default=lambda self:(datetime.now() + timedelta(days=(1))))
    coverage_to = fields.Date('To')
    days = fields.Integer('Day(s)',compute='compute_days',store='True')
    geographical_coverage = fields.Selection([('zone 1', 'Europe'),
                                              ('zone 2', 'Worldwide excluding USA & CANADA'),
                                              ('zone 3', 'Worldwide'), ],
                                             'Zone',
                                             default='zone 1')

    currency_id = fields.Many2one("res.currency", "Currency", copy=True,
                                  default=lambda self: self.env.user.company_id.currency_id, readonly=True)
    net_premium = fields.Float('Net Premium',  )
    proportional_stamp = fields.Float('Proportional Stamp', )
    dimensional_stamp = fields.Float('Dimensional Stamp', )
    supervisory_stamp = fields.Float('Supervisory Stamp', )
    policy_approval_fees = fields.Float('Policy approval fees', )
    policy_holder_fees = fields.Float('Policyholder’s protection fees',)
    admin_fees = fields.Float('Admin Fees', )
    issue_fees = fields.Float('Issue Fees',)
    gross_premium = fields.Float('Gross Premium')
    # travel_agent = fields.Many2one('travel.agency', 'Travel Agency',force_save="1")
    travel_agency = fields.Many2one('travel.agency', 'Travel Agency',store=True, force_save="1"
                                    )
    travel_agency_branch = fields.Many2one('agency.branch', 'Agency Branch',
                                           domain="[('travel_agency','=',travel_agency)]",
                                            readonly=True)
    user_id = fields.Many2one('res.users', 'User Name', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user, readonly=True)
    duration=fields.Selection('_get_periods',string='Duration',store=True)
    cancel_reason = fields.Char('Cancel Reason')
    travel_agency_comm = fields.Float('Agency Commission')
    agent_commission=fields.Float('commission')
    broker_commission=fields.Float('Broker commission', )
    bonus_commission=fields.Float('Bonus Commission')

    net_to_insurer = fields.Float('Net To Insurer', compute='get_financial_data',store=True)
    is_canceled = fields.Boolean(default=False)
    family_age = fields.One2many('policy.family.age','policy_id', ondelete='cascade', string='Family Age')
    # special_beneifts = fields.Many2many('travel.benefits',string='Special Benefits',domain="[('special_covers', '=', True)]")

    price_details = fields.Boolean('Show Price Details In Policy', default=False)
    country = fields.Many2one('res.country', 'Destination')

    @api.onchange('duration')
    def compute_agency(self):
        # if self.user_id.travel_agency:
            self.travel_agency = self.create_uid.travel_agency.id

    def test(self):
        self.send_mail_template('AhmedNourElhalaby@gmail.com')

    def check_soucre(self):
        return self.create_uid.has_group('smart_travel_agency.head_office_group')

    def _get_periods(self):
        #you Must Change
        options = []
        options_dict = []
        data = self.env['travel.price.line'].search([])
        for option in data:
            options.append(option.period)
        options = list(dict.fromkeys(options))
        for option in options:
                options_dict.append((str(option),str(option)+' Days'))
        return options_dict
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

    @api.onchange('package','coverage_from','coverage_to','DOB','product')
    def get_price_calculations(self):
        if self.product:
            self.get_financial_data()




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
    # @api.multi
    def print_report_xml(self):
        # data = {'start_date': self.start_date, 'end_date': self.end_date}
        return self.env.ref('smart_travel_agency.travel_xml_report').report_action(self)

    def get_financial_data(self):
        if self.age and self.geographical_coverage and self.days and self.product:
            # data = self.env['travel.price'].search(
            #     [('zone', '=', self.geographical_coverage)])
            result={}
            kid_dob=[]
            # if self.create
            # self.travel_agency =
            if self.days>0 :
                for rec in self.family_age:
                    if rec.type=='kid':
                       kid_dob.append(rec.DOB)
                # print(kid_dob)

                if self.package == 'individual':
                    result=self.get_individual({'product': self.product.id, 'z':self.geographical_coverage,'d':[self.DOB],'p_from':self.coverage_from,'p_to':self.coverage_to})


                elif self.package == 'family':
                    result=self.get_family({'product': self.product.id, 'z':self.geographical_coverage,'p_from':self.coverage_from,'p_to':self.coverage_to,'kid_dob':kid_dob})
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
                if self.broker and self.product:
                    commission = self.env['commission.table'].search([('product', 'in', [self.product.id])],limit=1)
                    for rec in commission:
                        if rec.broker and self.broker.id in rec.broker.ids:
                              self.broker_commission = self.net_premium * (rec.basic /100)
                              break
                        else:
                             self.broker_commission = self.net_premium * (rec.basic / 100)

                self.net_to_insurer = self.gross_premium - self.agent_commission
            else:
                raise UserError((
                    "Period Is Incorrect Or Age Is Incorrect "))



    @api.model
    def get_individual(self,data):
        if data.get('z') and data.get('d') and data.get('p_from') and data.get('p_to') and data.get('product'):
            result = {}
            # s_coverSum = 0
            # s_covers=[]
            # if data.get("s_covers"):
            #     s_covers = data.get('s_covers')
            #     s_coversList = self.env['travel.benefits'].search([("id", "in", s_covers)])
            #     for cover in s_coversList:
            #         s_coverSum += cover.cover_rate
            geographical_coverage=data.get('z')
            DOB=data.get('d')
            coverage_from=data.get('p_from')
            coverage_to=data.get('p_to')
            product = data.get('product')

            # dob=[DOB]
            days=self.calculate_period(coverage_from,coverage_to)
            age=self.calculate_age(DOB)

            data = self.env['travel.price'].search(
                [('product', '=', product),('zone', '=', geographical_coverage),('from_age','<=',age[0]),('to_age','>=',age[0])])

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
                                    result['policy_holder_fees'] = rec.policy_holder_fees
                                    result['policy_approval_fees'] = rec.policy_approval_fees
                                    # self.issue_fees = record.issue_fees
                                    fra,result['gross'] = math.modf(rec.gross_premium *(record.currency_id.rate))
                                    # result['oldgross']=result['gross']
                                    # if s_coverSum !=0.0:
                                    #     fra, result['gross'] = math.modf(result['gross']+(result['gross'] * s_coverSum))
                                    result['issue_fees'] = (rec.issue_fees *(record.currency_id.rate))+(1-fra)
                                    # result['s_coverSum']=s_coverSum
                                    # result['s_covers']=s_covers
                                    print("fraction")
                                    print (fra)

            return result

    @api.model
    def get_family(self,data):
        if data.get('z') and data.get('p_from') and data.get('p_to') and data.get('product'):
            # s_coverSum = 0
            # if data.get("s_covers"):
            #     s_covers = data.get('s_covers')
            #     s_coversList = self.env['travel.benefits'].search([("id", "in", s_covers)])
            #     for cover in s_coversList:
            #         s_coverSum += cover.cover_rate
            geographical_coverage = data.get('z')
            coverage_from = data.get('p_from')
            coverage_to = data.get('p_to')
            product = data.get('product')
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
                    res=self.get_individual({'product': product,'z':geographical_coverage,'d':[rec],'p_from':coverage_from,'p_to':coverage_to})
                    final_kid.append(res)
                    print('8888888888888888888888888888888888888888888888888888888888888888888888')
                print(res)

                print ('eslammmmmmmmmmmmmmmmmmmmmmmmmmmmmmm99999999999999')
                print(age[0])
            result = {}
            data = self.env['travel.price'].search(
                [('product', '=', product),('zone', '=',geographical_coverage),('package','=','family')])

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
                            result['policy_holder_fees'] = rec.policy_holder_fees
                            result['policy_approval_fees'] = rec.policy_approval_fees
                            # self.issue_fees = record.issue_fees
                            fra,result['gross'] = math.modf(record.gross_premium *(rec.currency_id.rate))
                            result['issue_fees'] = (record.issue_fees * (rec.currency_id.rate)) + (1 - fra)
                            result['oldgross']=result['gross']
                            # if s_coverSum != 0.0:
                            #     fra, result['gross'] = math.modf(result['gross'] + (result['gross'] * s_coverSum))
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
                   result['policy_holder_fees'] = record.get('policy_holder_fees') +result.get('policy_holder_fees')
                   result['policy_approval_fees'] = record.get('policy_approval_fees') +result.get('policy_approval_fees')
                   print(fra)
                   print('kid')
                   print(record)
                   print('final')

            return result

    @api.model
    def get_group(self,data):
        if data.get('zone') and data.get('p_from') and data.get('p_to') and data.get('product'):
            # s_coverSum = 0
            # if data.get("s_covers"):
            #     s_covers = data.get('s_covers')
            #     s_coversList = self.env['travel.benefits'].search([("id", "in", s_covers)])
            #     for cover in s_coversList:
            #         s_coverSum += cover.cover_rate
            days=self.calculate_period(data.get('p_from'),data.get('p_to'))
            result={'net':0.0,'pro_stamp':0.0,'dimensional_stamp':0.0,'supervisory_stamp':0.0,'gross':0.0,'issue_fees':0.0}
            discount=0.0
            for group in data.get('group'):
               price_discount=self.env['group.discount'].search(
                  [('from_date','<=',datetime.today()),('to_date','>=',datetime.today()),('from_size', '<=',group['size']), ('to_size', '>=', group['size'])])
               if price_discount:
                   discount=price_discount.perc

               price = self.env['travel.price'].search(
                  [('product', '=', data.get('product')),('zone', '=', data.get('zone')), ('from_age', '<=',group['age']), ('to_age', '>=', group['age'])])

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
                                   result['oldgross']=result['gross']
                                   # if s_coverSum != 0.0:
                                   #     fra, result['gross'] = math.modf(result['gross'] + (result['gross'] * s_coverSum))

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
    @api.model
    @api.constrains('duration','geographical_coverage')
    def _check_period(self):
        if int(int(self.duration)/365) >2 and self.geographical_coverage !='zone 1':
            raise exceptions.ValidationError('Duration Error For This Region')

    @api.constrains('national_id')
    def _check_national(self):
        if self.national_id:
            if self.national_id[1:3] != str(self.DOB).split('-')[0][-2:] or self.national_id[3:5] != str(self.DOB).split('-')[1] or self.national_id[5:7] != str(self.DOB).split('-')[2]:
                raise exceptions.ValidationError('National id not Matching Date of Birth')
            if len(str(self.national_id))!=14:
                raise exceptions.ValidationError('Invalid Must Be 14 Characters')

    # @api.constrains('age')
    def _check_contract_period(self):
        if self.travel_agency:
            if self.travel_agency.contract_to <= self.issue_date.date():
               raise exceptions.ValidationError('Contract Period Invalid')


    # @api.multi
    def confirm_policy(self):
        if self.address and self.insured and self.passport_num and self.DOB and self.gender and self.geographical_coverage and self.days:
            self.get_financial_data()
            self._check_contract_period()
            self._check_national()
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
        benefits = []
        product = self.env['travel.price'].search(
                [('product', '=', self.product.id),('zone', '=', self.geographical_coverage)], limit=1)
        for rec in product.covers:
            benefits.append(rec)
        return benefits
        # return self.env['travel.benefits'].search([('special_covers', '=', False)])

    def get_special_benefits(self):
        benefits = []
        product = self.env['travel.price'].search(
            [('product', '=', self.product.id), ('zone', '=', self.geographical_coverage)], limit=1)
        for rec in product.covers:
            if rec.special_covers == True:
                benefits.append(rec)
        return benefits

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
    relationship = fields.Many2one('family.members', 'Relationship')

    gender = fields.Selection([('M', 'Male'), ('F', 'Female')])
    age=fields.Float('age')
    DOB = fields.Date('Date Of Birth',required=True)
    pass_num = fields.Char('Passport',required=True)
    # @api.one
    @api.constrains('age')
    def _check_age(self):
        for rec in self:
            if rec.age:
                if rec.age>18 and rec.type=='kid':
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


class TrackOrders(models.Model):
    _name = 'orders'
    _rec_name = 'order_id'

    order_id = fields.Char(string='Order ID', required=True, copy=False, index=True,
                             default=lambda self: self.env['ir.sequence'].next_by_code('order'), readonly=True)

class FamilyMembersAgeSetyp(models.Model):
    _name = 'family.members'
    _rec_name = 'relationship'
    relationship = fields.Char('Relationship')
    from_age = fields.Integer('From Age')
    to_age = fields.Integer('To Age')

    @api.model
    def get_family_members(self):
        result = []
        for rec in self.env['family.members'].search([]):
            result.append({'type': rec.relationship, 'from_age': rec.from_age, 'to_age': rec.to_age})
        return result


