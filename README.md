# Django NoSQL objects
Django app that provides a simple REST API for storing and querying JSON documents.

# Package requirements
- django-filter
- django-guardian
- djangorestframework
- djangorestframework-guardian

# Installing
Add the following apps in your settings.py:

```python
INSTALLED_APPS = (
    ...
    "rest_framework",
    "django_filters",
    "guardian"
    "nosql_objects",
    ...
)
```

Add the following routes in urls.py:

```python
urlpatterns = [
    ...
    path('api/', include('nosql_objects.urls')),
    ...
]
```





# Querying

## Pagination
Pagination is used to limit the amount of results returns while querying

# Permissions

## Groups

## Anonymous