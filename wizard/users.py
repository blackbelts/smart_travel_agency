from datetime import timedelta, datetime
import base64
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import api, fields, models

class AgentUsersWizard(models.TransientModel):
    _inherit = 'person.user.wizard'

    branch=fields.Boolean(default=False)
    travel_agency = fields.Many2one('travel.agency', 'Travel Agency')
    travel_agency_branch = fields.Many2one('agency.branch', 'Agency Branch')

    # @api.multi
    def generate_users(self):
        self.env['res.users'].create({'name': self.name, 'login': self.name,'password':self.password,
                                      'sel_groups_1_8_9' : '1','in_group_17': True})
            #                           'groups_id': [
            # self.env['res.groups'].search([('name', '=', 'User: All Agency Documents')]).id]})

    # @api.multi
    def generate_branch_users(self):
        self.env['res.users'].create({'name': self.name+'-'+str(self.travel_agency.agency_code),
                                      'login': self.name+'-'+str(self.travel_agency.agency_code),
                                      'travel_agency_branch':self.id,'travel_agency':self.travel_agency.id,
                                      'password': self.password,'sel_groups_1_8_9' : '1','in_group_16': True})
            #                           'groups_id': [
            # self.env['res.groups'].search([('name', '=', 'User: Own Documents')]).id]})
