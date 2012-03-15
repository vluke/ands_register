# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context
from django.shortcuts import render_to_response, redirect
from django.views.decorators.cache import never_cache

from tardis.tardis_portal.auth import decorators as authz
from tardis.tardis_portal.creativecommonshandler import CreativeCommonsHandler
from tardis.tardis_portal.models import Experiment
from tardis.tardis_portal.shortcuts import render_response_index


from . import forms
from . import publishing

import logging
logger = logging.getLogger(__name__)


@never_cache
@authz.experiment_access_required
def index(request, experiment_id):
    url = 'ands_register/index.html'

    e = Experiment.objects.get(pk=experiment_id)
    cch = CreativeCommonsHandler(experiment_id=experiment_id, create=False)
    has_licence = cch.has_cc_license()
    is_owner = authz.has_experiment_ownership(request, experiment_id)

    if request.POST:
        if not is_owner:
            return return_response_error(request)

        publish_handler = publishing.PublishHandler(experiment_id, True)
        form = forms.PublishingForm(has_licence, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            publish_handler.update(cleaned_data)
            return HttpResponse('{"success": true}', mimetype='application/json')
    else:
        publish_handler = publishing.PublishHandler(experiment_id)
        form = forms.PublishingForm(has_licence, initial=publish_handler.form_data_with_abstract())

    c = Context()
    c['is_owner'] = is_owner
    c['has_licence'] = has_licence
    c['experiment'] = e
    c['form'] = form

    custom_desc = publish_handler.custom_description()
    
    # The following few lines handle the special case of only "<" and ">"
    # are in the custom description field 
    if custom_desc == ">":
        c['custom_description'] = "&gt;"
    elif custom_desc == "<":
        c['custom_description'] = "&lt;"
    else:
        c['custom_description'] = custom_desc

    authors = [a.author for a in e.author_experiment_set.all()]
    c['authors_csv'] = ', '.join(authors)

    custom_authors = publish_handler.custom_authors()
    if custom_authors:
        c['custom_authors_csv'] = ', '.join(custom_authors)

    c['access_type'] = publish_handler.access_type()

    return HttpResponse(render_response_index(request, url, c))
