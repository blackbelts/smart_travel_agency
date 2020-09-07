# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import babel.messages.pofile
import base64
import datetime
import functools
import glob
import hashlib
import imghdr
import io
import itertools
import jinja2
import json
import logging
import operator
import os
import re
import sys
import tempfile
import time
import zlib

import werkzeug
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict
from werkzeug.urls import url_decode, iri_to_uri
from xml.etree import ElementTree
import unicodedata
from odoo import models, fields, api
import odoo
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_resource_path
# from odoo.tools import crop_image, topological_sort, html_escape, pycompat
# from odoo.tools.translate import _
# from odoo.tools.misc import str2bool, xlwt, file_open
# from odoo.tools.safe_eval import safe_eval
# from odoo import http
# from odoo.http import content_disposition, dispatch_rpc, request, \
#     serialize_exception as _serialize_exception, Response
# from odoo.exceptions import AccessError, UserError
# from odoo.models import check_method_name
# from odoo.service import db
import webbrowser
from urllib.request import urlopen
import urllib.request

# _logger = logging.getLogger(__name__)


class CrmBlackBelts(http.Controller):
    @http.route('/report/<int:recid>', auth='public',cors='*')
    def reportdwoan(self, **kw):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        context = dict(request.env.context)
        values = kw.get('recid')
        report = request.env['ir.actions.report'].sudo()._get_report_from_name('smart_travel_agency.policy')
        pdf = report.with_context(context).render_qweb_pdf(values)[0]
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

     