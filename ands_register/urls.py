from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    'tardis.apps.as_ands.views',
    (r'^(?P<experiment_id>\d+)/$', 'index'),
    )

