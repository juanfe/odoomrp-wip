
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################


from openerp import _
from openerp.osv import fields, osv


class Machinery(osv.Model):
    _name = "machinery"
    _description = "Holds records of Machines"

    def _def_company(self):
        return self.env.user.company_id.id

    _columns = {
        'name': fields.char('Machine Name', required=True),
        'company': fields.many2one('res.company', 'Company', required=True,
                              default=_def_company),
        'assetacc': fields.many2one('account.account', string='Asset Account'),
        'depracc': fields.many2one('account.account',
                                   string='Depreciation Account'),
        'year': fields.char('Year'),
        'model': fields.char('Model'),
        'product': fields.many2one( 'product.product',
                                    string='Associated product',
                                    help="This product will contain "
                                         "information about the machine such "
                                         "as the manufacturer."),
        'manufacturer': fields.many2one('res.partner',
                                        related='product.manufacturer',
                                        readonly=True, help="Manufacturer is "
                                            "related to the associated product"
                                            " defined for the machine."),
        'serial_char': fields.char('Product Serial #'),
        'serial': fields.many2one('stock.production.lot', string='Product Serial #',
                             domain="[('product_id', '=', product)]"),
        'model_type': fields.many2one('machine.model', 'Type'),
        'status': fields.selection([('active', 'Active'), ('inactive', 'InActive'),
                               ('outofservice', 'Out of Service')],
                              'Status', required=True, default='active'),
        'ownership': fields.selection([('own', 'Own'), ('lease', 'Lease'),
                                  ('rental', 'Rental')],
                                 'Ownership', default='own', required=True),
        'bcyl': fields.float('Base Cycles', digits=(16, 3),
                        help="Last recorded cycles"),
        'bdate': fields.date('Record Date',
                        help="Date on which the cycles is recorded"),
        'purch_date': fields.date('Purchase Date',
                             help="Machine's date of purchase"),
        'purch_cost': fields.float('Purchase Value', digits=(16, 2)),
        'purch_partner': fields.many2one('res.partner', 'Purchased From'),
        'purch_inv': fields.many2one('account.invoice', string='Purchase Invoice'),
        'purch_cycles': fields.integer('Cycles at Purchase'),
        'actcycles': fields.integer('Actual Cycles'),
        'deprecperc': fields.float('Depreciation in %', digits=(10, 2)),
        'deprecperiod': fields.selection([('monthly', 'Monthly'),
                                     ('quarterly', 'Quarterly'),
                                     ('halfyearly', 'Half Yearly'),
                                     ('annual', 'Yearly')], 'Depr. period',
                                    default='annual', required=True),
        'primarymeter': fields.selection([('calendar', 'Calendar'),
                                     ('cycles', 'Cycles'),
                                     ('hourmeter', 'Hour Meter')],
                                    'Primary Meter', default='cycles',
                                    required=True),
        'warrexp': fields.date('Date', help="Expiry date for warranty of product"),
        'warrexpcy': fields.integer('(or) cycles',
                               help="Expiry cycles for warranty of product"),
        'location': fields.many2one('stock.location', 'Stk Location',
                               help="This association is necessary if you want"
                               " to make repair orders with the machine"),
        'enrolldate': fields.date('Enrollment date', required=True,
                             default=lambda
                             self: fields.date.context_today(self)),
        'ambit': fields.selection([('local', 'Local'), ('national', 'National'),
                              ('international', 'International')],
                             'Ambit', default='local'),
        'card': fields.char('Card'),
        'cardexp': fields.date('Card Expiration'),
        'frame': fields.char('Frame Number'),
        'phone': fields.char('Phone number'),
        'mac': fields.char('MAC Address'),
        'insurance': fields.char('Insurance Name'),
        'policy': fields.char('Machine policy'),
        'users': fields.one2many('machinery.users', 'machine', 'Machine Users'),
        'power': fields.char('Power (Kw)'),
    }


class MachineryUsers(osv.Model):
    _name = 'machinery.users'

    _columns = {
        'm_user': fields.many2one('res.users', 'User'),
        'machine': fields.many2one('machinery', 'Machine'),
        'start_date': fields.date('Homologation Start Date'),
        'end_date': fields.date('Homologation End Date'),
    }

    _sql_constraints = [
        ('uniq_machine_user', 'unique(machine, m_user)',
         _('User already defined for the machine'))
    ]
