# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


import os
import sys
import logging
import openerp
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)


class ProductImportXLSWizard(orm.TransientModel):
    ''' Wizard for
    '''
    _name = 'product.import.xls.wizard'

    # --------------------
    # Wizard button event:
    # --------------------
    def action_import(self, cr, uid, ids, context=None):
        ''' Event for button done
        '''
        if context is None: 
            context = {}                
        #wizard_browse = self.browse(cr, uid, ids, context=context)[0]
        
        # Import procedure:
        return {
            'type': 'ir.actions.act_window_close'
            }

    _columns = {
        'mode': fields.selection([
            ('update', 'Update mode (create new and update present)'),
            ('syncro', 'Syncro mode (create, update and delete not present'),
            ], 'Mode', required=True)
        }
        
    _defaults = {
        'mode': lambda *x: 'syncro',
        }    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


