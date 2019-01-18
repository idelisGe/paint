# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleUserReport(models.TransientModel):
    _name = 'sale.user.report'
    _description = 'Sale User Report'

    start_date = fields.Datetime(required=True, default=fields.Datetime.now)
    end_date = fields.Datetime(required=True, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', 'Vendedor', required=True)

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_report(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date', 'user_id'])[0]
        return self.env.ref('sale_premiumpaint.action_report_saleuser').report_action([], data=data)
