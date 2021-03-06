#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

from __future__ import division
from openmolar.settings import localsettings


def toHtml(plandata):
    '''
    returns an HTML table of the patients plandata
    '''
    if not plandata.retrieved:
        return "There was an error retrieving this information"

    retarg = '''<html><body><center>
    <h3>PLAN DETAILS</h3>
    <table width ="100%" border="1">
    '''
    retarg += "<tr><td>PLAN TYPE</td><td>%s</td></tr>" % plandata.plantype
    retarg += "<tr><td>BAND</td><td>%s</td></tr>" % plandata.band
    retarg += "<tr><td>GROSS CHARGE</td><td>%s</td></tr>" % (
        localsettings.formatMoney(plandata.grosschg))

    retarg += "<tr><td>DISCOUNT</td><td>%s&#37;</td></tr>" % plandata.discount
    retarg += "<tr><td>NET CHARGE</td><td>%s</td></tr>" % (
        localsettings.formatMoney(plandata.netchg))

    retarg += "<tr><td>CATEGORY</td><td>%s</td></tr>" % plandata.catcode
    retarg += "<tr><td>DATE JOINED</td><td>%s</td></tr>" % plandata.planjoin
    retarg += "<tr><td>REGISTRATION NUMBER</td><td>%s</td></tr>" % plandata.regno

    retarg += '</table></body></html>'

    return retarg

if __name__ == "__main__":
    from openmolar.dbtools import patient_class
    localsettings.initiate()
    try:
        serialno = int(sys.argv[len(sys.argv) - 1])
    except:
        serialno = 707

    pt = patient_class.patient(serialno)
    print toHtml(pt.plandata)
