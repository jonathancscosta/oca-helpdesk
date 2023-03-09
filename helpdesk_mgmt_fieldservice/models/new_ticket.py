from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'

    name = fields.Char(string='Ticket Subject', required=True)
    description = fields.Text(string='Description')
    customer_id = fields.Many2one('res.partner', string='Customer')
    team_id = fields.Many2one('helpdesk.team', string='Team')
    stage_id = fields.Many2one('helpdesk.stage', string='Stage')
    user_id = fields.Many2one('res.users', string='Assigned To')

    @api.model
    def create_ticket(self, subject, description, customer_id, team_id, stage_id, user_id):
        ticket = self.create({
            'name': subject,
            'description': description,
            'customer_id': customer_id,
            'team_id': team_id,
            'stage_id': stage_id,
            'user_id': user_id,
        })
        return ticket
from odoo import models, fields, api

class HelpdeskCategory(models.Model):
    _name = 'helpdesk.category'
    _description = 'Helpdesk Category'

    name = fields.Char(string='Name', required=True)

    @api.model
    def create_category(self, name):
        category = self.create({
            'name': name,
        })
        return category
