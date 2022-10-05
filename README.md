# Django NoSQL objects
Django app that provides a simple REST API for storing and querying JSON documents.

# Features
- Storing, querying, deleting schemaless JSON documents.
- Permission system that allows users define who can access their own documents.
- Query objects by their contents.
- Allow anonymous access to specific documents.
- REST API

# Package requirements
- django-filter
- django-guardian
- djangorestframework
- djangorestframework-guardian

# Installing
- Add the following apps in your settings.py:

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

- Add the following routes in urls.py:

```python
urlpatterns = [
    ...
    path('api/', include('nosql_objects.urls')),
    ...
]
```

- Execute migrations to add models to database.
```python
python manage.py migrate
```

# Object classes
Object classes define the types of objects that can be created in your application. 
These types are analogous to models in Django and tables in a database, and their main purpose is to delimit the schema of your objects when querying.
The declaration of this classes can be done trough the admin portal of Django.

# Creating new objects
Authorized users can create new objects like this:
```bash
curl -X POST -H "Content-Type: application/json" -d {{'{"object_class":"myClass", "data":{myInfo:"value"} }'}} {{http://yourdomain.com/api/objects/}}
```

# Querying
Clients can query their objects by filtering 



## By class

## Custom filtering

## Pagination
Pagination is used to limit the amount of results returns while querying

# Permissions

## Groups

## Anonymous