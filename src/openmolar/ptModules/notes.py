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

'''
This module is deprecated with schema version 1.9

It is, however, legacy code required for the upgrade schema process
'''


import datetime
import re
import sys
from openmolar.settings import localsettings

CHART = {
    136: "UR8", 135: "UR7", 134: "UR6", 133: "UR5",
    132: "UR4", 131: "UR3", 130: "UR2", 129: "UR1",
    144: "UL1", 145: "UL2", 146: "UL3", 147: "UL4",
    148: "UL5", 149: "UL6", 150: "UL7", 151: "UL8",
    166: "LL8", 165: "LL7", 164: "LL6", 163: "LL5",
    162: "LL4", 161: "LL3", 160: "LL2", 159: "LL1",
    174: "LR1", 175: "LR2", 176: "LR3", 177: "LR4",
    178: "LR5", 179: "LR6", 180: "LR7", 181: "LR8",
    142: "URE", 141: "URD", 140: "URC", 139: "URB",
    138: "URA", 153: "ULA", 154: "ULB", 155: "ULC",
    156: "ULD", 157: "ULE", 172: "LLE", 171: "LLD",
    170: "LLC", 169: "LLB", 168: "LLA", 183: "LRA",
    184: "LRB", 185: "LRC", 186: "LRD", 187: "LRE"}


def rec_notes(notes_dict):
    '''
    returns an html string of notes, designed to fit into the
    reception notes panel (ie. vertical)
    '''

    retarg = '''<html><head><link rel="stylesheet"
    href="%s" type="text/css"></head><body>''' % localsettings.stylesheet
    keys = sorted(notes_dict.keys())

    previousdate = ""  # necessary to group notes on same day
    divopen = False
    for key in keys:
        date, op = key
        notes = get_notes_for_date(notes_dict[key])
        d = get_date_from_date(date)
        ests = get_estimate_for_date(notes_dict[key])
        rec = get_reception_for_date(notes_dict[key])
        if ests or rec:
            if d != previousdate:
                previousdate = d
                retarg += '<div class="recep_date">%s' % d
                divopen = True

            retarg += "<ul>"
            if ests:
                retarg += '<li class="recep_note">%s</li>' % ests
            if rec:
                rec = rec.replace("<li>", '<li class="recep_note">')
                rec = rec.replace("PRINTED:",
                                  '<img src=%s height="12" align="left">' % (
                                      localsettings.printer_png))
                rec = rec.replace("RECEIVED:",
                                  '<img src=%s height="12" align="left">' % (
                                      localsettings.money_png))
                retarg += rec
            retarg += "</ul>"
        if divopen:
            retarg += "</div>"
            divopen = False

    retarg += '</body></html>'

    return retarg


def notes(notes_dict, verbosity=0, ignoreRec=False):
    '''
    returns an html string of notes...
    if verbose=1 you get reception stuff too.
    if verbose =2 you get full notes
    '''

    retarg = '''<html><head><link rel="stylesheet"
    href="%s" type="text/css"></head><body>''' % localsettings.stylesheet
    keys = sorted(notes_dict.keys())
    retarg += '''<table>
    <tr>
        <th>Date</th>
        <th>ops</th>
        <th>Tx</th>
        <th>Notes</th>
    '''

    if verbosity > 0:
        retarg += '<th>reception</th>'

    if verbosity == 2:  # this is for development/debugging purposes
        retarg += '<th>Detailed</th>'

    retarg += '</tr>'
    wstring = "70%"

    previousdate = ""  # necessary to group notes on same day
    rowspan = 1
    newline = ""
    for key in keys:
        date, op = key
        notes = get_notes_for_date(notes_dict[key])
        if ("REC" in op and notes != "") or (
                "REC" in op and not ignoreRec) or not "REC" in op:
            newline += "<tr>"
            d = get_date_from_date(date)
            if d != previousdate:
                previousdate = d
                rowspan = 1
                retarg += newline
                newline = '<td class="date">%s</td>' % d
            else:
                # alter the previous html, so that the rows are spanned
                rowspan += 1
                newline = re.sub(
                    'class="date"( rowspan="\d")*',
                    'class="date" rowspan="%d"' % rowspan, newline)

            newline += '''<td class="ops">%s</td>
            <td class="tx">%s</td><td width="%s" class="notes">%s</td>''' % (
                op, get_codes_for_date(notes_dict[key]),
                wstring, notes)

            ests = get_estimate_for_date(notes_dict[key])
            rec = get_reception_for_date(notes_dict[key])
            if verbosity > 0:
                newline += '<td class="reception">'
                if rec != "" and ests == "":
                    newline += '%s</td>' % rec
                elif rec == "" and ests != "":
                    newline += '%s</td>' % ests
                else:
                    newline += "%s<br />%s</td>" % (ests, rec)

            if verbosity == 2:
                text = ""
                for item in notes_dict[key]:
                    text += "%s<br />" % str(item)
                newline += "<td class=verbose>%s</td>" % text

            newline += "</tr>"
    retarg += newline
    retarg += '</table></div></body></html>'

    return retarg


def get_date_from_date(key):
    '''
    converts to a readable date
    '''
    try:
        k = key.split('_')
        d = datetime.date(int(k[0]), int(k[1]), int(k[2]))
        return localsettings.formatDate(d)
        # return k[2]+"/"+k[1]+"/"+k[0]
    except IndexError:
        return "IndexERROR converting date %s" % key
    except ValueError:
        return "TypeERROR converting date %s" % key


def get_codes_for_date(line):
    code = ""
    for l in line:
        if "TC" in l[0]:
            code += "<b>"
            tx = l[1]
            while len(tx) > 8 and " " in tx[8:]:
                pos = tx.index(" ", 8)
                code += "%s <br />" % tx[:pos]
                tx = tx[pos:]
            code += "%s </b>" % tx
    if code == "":
        return "-"
    else:
        return code


def get_notes_for_date(line):
    '''
    this is the actual user entered stuff!
    '''
    note = ""
    for l in line:
        if "NOTE" in l[0]:
            mytext = l[1].replace("<", "&lt;").replace(">", "&gt;")
            note += "%s " % mytext
    match = re.search(r"[\n ]*$", note)
    if match:
        note = note[:note.rindex(match.group())]
    return note.replace("\n", "<br />")


def get_reception_for_date(line):
    '''
    was anything printed etc....
    '''
    recep = ""
    for action, value, user in line:
        value = value.replace("sundries 0.00", "")
        value = value.replace("==========", "")
        if (("PRINT" in action) or ("RECEIVED" in action) or
           ("FINAL" in action) or ("UNKNOWN" in action) or
                ("UPDATE" in action) or ("COURSE" in action)):
            recep += "<li>%s %s</li>" % (action, value)
    return recep


def get_estimate_for_date(line):
    est = ""
    for l in line:
        if "ESTIMATE" in l[0]:
            est += "%s%s" % (l[0], l[1])
    return est


def decipher_noteline(noteline):
    '''
    returns a list.  ["type","note","operator","date"]
    '''
    retarg = ["", "", "", ""]

    if len(noteline) == 0:  # sometimes a line is blank
        return retarg

    # important - this line give us operator and date.
    if noteline[0] == chr(1):
        retarg[0] = "opened"
        operator = ""
        i = 1
        while noteline[i] >= "A" or noteline[i] == "/":
            operator += noteline[i]
            i += 1

        # arghh!!! 2 character year field!!!!!!
        workingdate = "%s_%02d_%02d" % (
            1900 + char(noteline[i + 2]), char(noteline[i + 1]), char(noteline[i]))

        retarg[2] = operator
        retarg[3] = workingdate
        try:
            systemdate = "%s/%s/%s" % (
                char(noteline[i + 3]), char(noteline[i + 4]),
                1900 + char(noteline[i + 5]))

            # systemdate includes time
            systemdate += " %02d:%02d" % (
                char(noteline[i + 6]), char(noteline[i + 7]))

            retarg[1] += "System date - %s" % systemdate

        except IndexError as e:
            print "error getting system date for patient notes - %s", e
            retarg[1] += "System date - ERROR!!!!!"

    elif noteline[0] == "\x02":   #
        retarg[0] = "closed"
        operator = ""
        i = 1
        while noteline[i] >= "A" or noteline[i] == "/":
            operator += noteline[i]
            i += 1
        systemdate = "%s/%s/%s" % (
            char(noteline[i]), char(noteline[i + 1]),
            1900 + char(noteline[i + 2]))

        systemdate += " %02d:%02d" % (
            char(noteline[i + 3]), char(noteline[i + 4]))

        retarg[1] += "%s %s" % (operator, systemdate)

    elif noteline[0] == chr(3):
        #-- hidden nodes start with chr(3) then another character
        if noteline[1] == chr(97):
            retarg[0] = "COURSE CLOSED"
            retarg[1] = "=" * 10
        elif noteline[1] == chr(100):
            retarg[0] = "UPDATED:"
            retarg[1] = "Medical Notes " + noteline[2:]
        elif noteline[1] == chr(101):
            retarg[0] = "UPDATED:"
            retarg[1] = "Perio Chart"
        elif noteline[1] == chr(104):
            retarg[0] = "TC: XRAY"
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(105):
            retarg[0] = "TC: PERIO"
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(106):
            retarg[0] = "TC: ANAES"
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(107):
            retarg[0] = "TC: OTHER"
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(108):
            retarg[0] = "TC: NEW Denture Upper"
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(109):
            retarg[0] = "TC: NEW Denture Lower"
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(110):
            retarg[0] = "TC: Existing Denture Upper"
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(111):
            retarg[0] = "TC: Existing Denture Lower"
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(112):
            retarg[0] = "TC: EXAM"
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(113):
            retarg[0] = "TC:"
            retarg[1] = tooth(noteline[2:])
        elif noteline[1] == chr(114):
            retarg[
                0] = "STATIC: "  # (1st line):"
            retarg[1] = tooth(noteline[2:])
        elif noteline[1] == chr(115):
            retarg[0] = "PRINTED: "
            retarg[1] = "GP17(A)"
        elif noteline[1] == chr(116):
            retarg[0] = "PRINTED: "
            retarg[1] = "GP17(C)"
        elif noteline[1] == chr(117):
            retarg[0] = "PRINTED: "
            retarg[1] = "GP17(DC)"
        elif noteline[1] == chr(119):
            retarg[0] = "RECEIVED: "
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(120):
            retarg[0] = "REVERSE PAYMENT:"
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(121):
            retarg[
                0] = "STATIC: "  # (additional Line):"
            retarg[1] = tooth(noteline[2:])
        elif noteline[1] == chr(123):
            retarg[0] = "PRINTED: "
            retarg[1] = "GP17"
        elif noteline[1] == chr(124):
            retarg[0] = "PRINTED: "
            retarg[1] = "GP17PR"
        elif noteline[1] == chr(130):
            retarg[0] = "ESTIMATE: "
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(131):
            retarg[0] = "INTERIM: "
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(132):
            retarg[0] = "FINAL: "
            retarg[1] = noteline[2:]
        elif noteline[1] == chr(133):
            retarg[0] = "ACTUAL: "
            retarg[1] = tooth(noteline[2:])
        elif noteline[1] == chr(134):
            retarg[0] = "FILED: "
            retarg[1] = "Claim"
        elif noteline[1] == chr(136):
            retarg[0] = "FILED: "
            retarg[1] = "Registration"
        elif noteline[1] == "v":
            retarg[0] = "PRINTED: "
            retarg[1] = noteline[2:]

        elif noteline[1] == chr(125):
            retarg[0] = "PRINTED: "
            retarg[1] = "GP17RA"

        elif noteline[1] == chr(98):
            retarg[0] = "WYSDOM ERROR: "
            retarg[1] = "PREVIOUS NOTES LOST"

        else:
            retarg[0] = 'UNKNOWN LINE: '
            retarg[1] += "%s  |  " % noteline[1:]
            for ch in noteline[1:]:
                retarg[1] += "'%s' " % str(char(ch))

        if "TC" in retarg[0]:
            retarg[1] = "%s" % retarg[1]

    elif noteline[0] == "\t":
        # this is the first character of any REAL line of old (pre MYSQL) notes
        retarg[0] = "oldNOTE"
        retarg[1] = "%s" % noteline[1:]
    else:
        # new note lines don't have the tab
        retarg[0] = "newNOTE"
        retarg[1] += "%s" % noteline
    return retarg


def char(c):
    i = 0
    while i < 256:
        if chr(i) == c:
            return i
            break
        i += 1


def tooth(data):
    # return str(data.split("\t"))
    retarg = ""
    for c in data:
        i = char(c)
        if i in CHART:
            retarg += CHART[i] + " "
        else:
            retarg += c
    return retarg


if __name__ == "__main__":
    sys.path.append("/home/neil/openmolar")
    from openmolar.dbtools import patient_class
    try:
        serialno = int(sys.argv[len(sys.argv) - 1])
    except:
        serialno = 1
    if "-v" in sys.argv:
        verbose = True
    else:
        verbose = False
    # print "getting notes"
    # print rec_notes(patient_class.patient(serialno).notes_dict)
    print notes(patient_class.patient(serialno).notes_dict, verbose)
