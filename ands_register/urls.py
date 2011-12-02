from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    'tardis.apps.ands_register.views',
    (r'^(?P<experiment_id>\d+)/$', 'index'),
    )

