# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.tools.translate import _
#from openerp.addons import decimal_precision as dp
from openerp import api
from openerp.osv import fields, osv


class MrpRouting(osv.Model):
    _inherit = 'mrp.routing'

    @api.one
    @api.constrains('workcenter_lines')
    def _check_produce_operation(self):
        if not self.workcenter_lines:
            return
        num_produce = sum([x.do_production for x in self.workcenter_lines])
        if num_produce != 1:
            raise Warning(_("There must be one and only one operation with "
                            "'Produce here' check marked."))


class MrpRoutingWorkcenter(osv.Model):
    _inherit = 'mrp.routing.workcenter'

    _columns = {
        'operation': fields.many2one('mrp.routing.operation', string='Operation'),
        'op_wc_lines': fields.one2many(
            'mrp.operation.workcenter', 'routing_workcenter',
            string='Possible work centers for this operation'),
        'do_production': fields.boolean(
            string='Produce here',
            help="If enabled, the production and movement to stock of the final "
                 "products will be done in this operation. There can be only one "
                 "operation per route with this check marked."),
    }

    @api.constrains('op_wc_lines')
    def _check_default_op_wc_lines(self):
        if not self.op_wc_lines:
            return
        num_default = len([x for x in self.op_wc_lines if x.default])
        if num_default != 1:
            raise Warning(
                _('There must be one and only one line set as default.'))

    @api.one
    @api.onchange('operation')
    def onchange_operation(self):
        if self.operation:
            self.name = self.operation.name
            self.note = self.operation.description
            op_wc_lst = []
            for operation_wc in self.operation.workcenters:
                data = {
                    'workcenter': operation_wc.id,
                    'capacity_per_cycle': operation_wc.capacity_per_cycle,
                    'time_efficiency': operation_wc.time_efficiency,
                    'time_cycle': operation_wc.time_cycle,
                    'time_start': operation_wc.time_start,
                    'time_stop': operation_wc.time_stop,
                    'op_number': self.operation.op_number,
                }
                op_wc_lst.append(data)
            op_wc_lst[0]['default'] = True
            self.op_wc_lines = op_wc_lst

    @api.one
    @api.onchange('op_wc_lines')
    def onchange_lines_default(self):
        for line in self.op_wc_lines:
            if line.default:
                self.workcenter_id = line.workcenter
                self.cycle_nbr = line.capacity_per_cycle
                self.hour_nbr = line.time_cycle
                break


class MrpOperationWorkcenter(osv.Model):
    _name = 'mrp.operation.workcenter'
    _description = 'MRP Operation Workcenter'

    _columns = {
        'workcenter': fields.many2one(
            'mrp.workcenter', string='Workcenter', required=True),
        'routing_workcenter': fields.many2one(
            'mrp.routing.workcenter', 'Routing workcenter', required=True),
        'time_efficiency': fields.float('Efficiency factor'),
        'capacity_per_cycle': fields.float('Capacity per cycle'),
        'time_cycle': fields.float('Time for 1 cycle (hours)',
                                  help="Time in hours for doing one cycle."),
        'time_start': fields.float('Time before prod.',
                                  help="Time in hours for the setup."),
        'time_stop': fields.float('Time after prod.',
                                 help="Time in hours for the cleaning."),
        'op_number': fields.integer('# operators', default='0'),
        'op_avg_cost': fields.float(
            string='Operator avg. cost'),
        # TODO checke the dp.get_precision, how to do
        #    digits=dp.get_precision('Product Price')),
        'default': fields.boolean('Default'),
    }

    @api.one
    @api.onchange('workcenter')
    def onchange_workcenter(self):
        if self.workcenter:
            self.capacity_per_cycle = self.workcenter.capacity_per_cycle
            self.time_efficiency = self.workcenter.time_efficiency
            self.time_cycle = self.workcenter.time_cycle
            self.time_start = self.workcenter.time_start
            self.time_stop = self.workcenter.time_stop
            self.op_number = self.workcenter.op_number
            self.op_avg_cost = self.workcenter.op_avg_cost
