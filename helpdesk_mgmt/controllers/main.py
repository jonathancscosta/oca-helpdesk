import base64
import logging

import werkzeug

import odoo.http as http
from odoo.http import request

_logger = logging.getLogger(__name__)


class HelpdeskTicketController(http.Controller):https://www.novitatus.com/
    @http.route("/ticket/close", type="http", auth="user")
    def support_ticket_close(self, **kw):
        """Close the support ticket"""
        values = {}
        for field_name, field_value in kw.items():
            if field_name.endswith("_id"):
                values[field_name] = int(field_value)
            else:
                values[field_name] = field_value
        ticket = (
            http.request.env["helpdesk.ticket"]
            .sudo()
            .search([("id", "=", values["ticket_id"])])
        )
        ticket.stage_id = values.get("stage_id")

        return werkzeug.utils.redirect("/my/ticket/" + str(ticket.id))

    def _get_teams(self):
        return (
            http.request.env["helpdesk.ticket.team"]
            .sudo()
            .search([("active", "=", True), ("show_in_portal", "=", True)])
            if http.request.env.user.company_id.helpdesk_mgmt_portal_select_team
            else False
        )

    @http.route("/new/ticket", type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):
        categories = http.request.env["helpdesk.ticket.category"].search(
            [("active", "=", True)]
        )
        email = http.request.env.user.email
        name = http.request.env.user.name
        return http.request.render(
            "helpdesk_mgmt.portal_create_ticket",
            {
                "categories": categories,
                "teams": self._get_teams(),
                "email": email,
                "name": name,
            },
        )

    def _prepare_submit_ticket_vals(self, **kw):
        category = http.request.env["helpdesk.ticket.category"].browse(
            int(kw.get("category"))
        )
        company = category.company_id or http.request.env.user.company_id
        vals = {
            "company_id": company.id,
            "category_id": category.id,
            "description": kw.get("description"),
            "name": kw.get("subject"),
            "attachment_ids": False,
            "channel_id": request.env["helpdesk.ticket.channel"]
            .sudo()
            .search([("name", "=", "Web")])
            .id,
            "partner_id": request.env.user.partner_id.id,
            "partner_name": request.env.user.partner_id.name,
            "partner_email": request.env.user.partner_id.email,
        }
        if company.helpdesk_mgmt_portal_select_team:
            team = (
                http.request.env["helpdesk.ticket.team"]
                .sudo()
                .search(
                    [("id", "=", int(kw.get("team"))), ("show_in_portal", "=", True)]
                )
            )
            vals.update({"team_id": team.id})
        return vals

    @http.route("/submitted/ticket", type="http", auth="user", website=True, csrf=True)
    def submit_ticket(self, **kw):
        vals = self._prepare_submit_ticket_vals(**kw)
        new_ticket = request.env["helpdesk.ticket"].sudo().create(vals)
        new_ticket.message_subscribe(partner_ids=request.env.user.partner_id.ids)
        if kw.get("attachment"):
            for c_file in request.httprequest.files.getlist("attachment"):
                data = c_file.read()
                if c_file.filename:
                    request.env["ir.attachment"].sudo().create(
                        {
                            "name": c_file.filename,
                            "datas": base64.b64encode(data),
                            "res_model": "helpdesk.ticket",
                            "res_id": new_ticket.id,
                        }
                    )
        return werkzeug.utils.redirect("/my/ticket/%s" % new_ticket.id)
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
from odoo import models, fields

class HelpdeskCategory(models.Model):
    _name = 'helpdesk.category'
    _description = 'Helpdesk Category'

    name = fields.Char(string='Name', required=True)
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
    category_id = fields.Many2one('helpdesk.category', string='Category')
category = self.env['helpdesk.category'].create({'name': 'Billing'})
ticket = self.env['helpdesk.ticket'].create({
    'name': 'Issue with the billing',
    'description': 'I have been charged twice for the same invoice',
    'customer_id': customer_id,
    'team_id': team_id,
    'stage_id': stage_id,
    'user_id': user_id,
    'category_id': category.id
})
