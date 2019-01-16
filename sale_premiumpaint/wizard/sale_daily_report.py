# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleDailyReport(models.TransientModel):
    _name = 'sale.daily.report'
    _description = 'Sale Daily Report'

    compute_at_date = fields.Selection([
        (0, 'Al dia'),
        (1, 'A una Fecha')
    ], string="Reporte", help="Reporte de hoy o de una determinada fecha")
    date = fields.Date('Fecha de reporte', help="Fecha para el reporte de ventas", default=fields.Datetime.now)

    def open_report(self):
        data = {}
        data['form'] = self.read(['compute_at_date', 'date'])[0]
        return self.env.ref('sale_premiumpaint.action_report_saledaily').report_action(self, data=data)
