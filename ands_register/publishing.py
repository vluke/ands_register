from tardis.tardis_portal.models import ExperimentParameterSet, Experiment, \
                                            ExperimentParameter
from tardis.tardis_portal.ParameterSetManager import ParameterSetManager

import logging
logger = logging.getLogger(__name__)

PUBLIC = 'public'
MEDIATED = 'mediated'
PRIVATE = 'private'
UNPUBLISHED = 'unpublished'


class PublishHandler(object):

    schema = "http://www.tardis.edu.au/schemas/sync_publish/2011/09/19"

    custom_description_key = 'custom_description'
    custom_authors_key = 'custom_authors'
    access_type_key = 'access_type'

    def __init__(self, experiment_id, create=False):
        self.experiment_id = experiment_id
        self.psm = self._get_or_create_publish_parameterset(create)

    def _get_or_create_publish_parameterset(self, create):
        parameterset = ExperimentParameterSet.objects.filter(
                        schema__namespace=self.schema,
                        experiment__id=self.experiment_id)

        if len(parameterset) == 1:
            psm = ParameterSetManager(parameterset=parameterset[0])
        elif create:
            experiment = Experiment.objects.get(id=self.experiment_id)
            psm = ParameterSetManager(schema=self.schema,
                    parentObject=experiment)
            psm.new_param(self.access_type_key, UNPUBLISHED)
        else:
            psm = None

        return psm

    def _get_or_none(self, key):
        if not self.psm:
            return None

        params = self.psm.get_params(key)
        if len(params) == 1:
            return params[0].string_value
        else:
            return None

    def access_type(self):
        return self._get_or_none(self.access_type_key) or UNPUBLISHED

    def custom_description(self):
        return self._get_or_none(self.custom_description_key)

    def custom_authors(self):
        if not self.psm:
            return []
        author_params = self.psm.get_params(self.custom_authors_key)
        return [a.string_value for a in author_params]

    def form_data(self):
        ''' 
        Use this method if you DO NOT want the custom description text area
        to be populated with the experiment description when no custom
        description is available.
        '''
        if not self.psm:
            return {}

        data = {}
        description = self.custom_description()
        if description:
            data[self.custom_description_key] = description
        authors = self.custom_authors()
        if authors:
            data[self.custom_authors_key] = ', '.join(authors)
        data[self.access_type_key] = self.access_type()

        return data
    
    def form_data_with_abstract(self):
        '''
        Use this method if you DO want the custom description text area
        to be populated with the experiment description when no custom
        description is available.
        '''
        experiment = Experiment.objects.get(id=self.experiment_id)
        if not self.psm:
            return {self.custom_description_key: experiment.description}

        data = {}
        description = self.custom_description()
        if description and description != "":
            data[self.custom_description_key] = description
        else:
            data[self.custom_description_key] = experiment.description
        authors = self.custom_authors()
        if authors:
            data[self.custom_authors_key] = ', '.join(authors)
        data[self.access_type_key] = self.access_type()

        return data

    def update(self, cleaned_data):
        ''' updates the publishing parameterset with the given form data'''
        self.psm.delete_all_params()
        to_save = {}
        to_save[self.access_type_key] = cleaned_data[self.access_type_key]
        if cleaned_data[self.custom_description_key]:
            description = cleaned_data[self.custom_description_key]
            to_save[self.custom_description_key] = description
        if cleaned_data[self.custom_authors_key]:
            authors = _split_authors(cleaned_data[self.custom_authors_key])
            to_save[self.custom_authors_key] = authors

        self.psm.set_params_from_dict(to_save)
        e = Experiment.objects.get(pk=self.experiment_id)
        if to_save[self.access_type_key] == PUBLIC:
            e.public = True
        else:
            e.public = False
        e.save()



def _split_authors(authors):
    authors = authors.split(',')
    authors = [a.strip() for a in authors]
    return authors
