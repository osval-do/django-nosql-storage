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

AUTHENTICATION_BACKENDS = (
    ...
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
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

# Authentication
Is recomended to add django-

# Creating new objects
Authorized users can create new objects like this:
```bash
curl -X POST -H "Content-Type: application/json" -d {{'{"object_class":"myClass", "data":{myInfo:"value"} }'}} {{http://yourdomain.com/api/objects/}}
```

# Querying
Clients can only query objects they read permission assigned. 
The following query will list all objects visible by the user:
```bash
curl http://yourdomain.com/api/objects/
```

## By class
Retriving objects on a class can be done by appending the class name in the query parameters:
 ```bash
curl http://yourdomain.com/api/objects/?object_class=my_class_name
```
Or with the unique ID of the class:
```bash
curl http://yourdomain.com/api/objects/?object_class=2
```

## Custom filtering

## Pagination
Pagination is used to limit the amount of results returned in querying requests. 
All the results contain the following structure:
```json
{
  "count": 5,
  "next": "https://api.example.org/accounts/?limit=100&offset=500",
  "previous": "https://api.example.org/accounts/?limit=100&offset=300",
  "results": [
    {
      "object_class": "scores",
      "created_by": 1,
      "updated_by": 1,
      "created_at": "...",
      "updated_at": "...",
      "version": 1,
      "data": { 
        "level1": 350
      }
    }
  ]
}
```

# Permissions
Each object contains its own list of permissions associated with it. Only users with the 'change' permission can change the permission list of an object.
The basic is the list of permissions `view_object`, `change_object` and `delete_object`. These are the same declared by Django, but custom permissions will be accepted too. Accessing the permissions endpoint is done using the ID of an existing object, like this:

```bash
curl -X POST -H "Content-Type: application/json" -d {{'{"view_object":{"users":["userB"]} }'}} {{http://yourdomain.com/api/objects/1/perms/}}
```

The permission endpoint **always** adds the permissions passed, unless the property `clear` is passed as true, then any permission is removed before adding the new ones.

The endpoint expects a json with the list of permissions with the users, groups or anonymous user  assigned (named 'AnonymousUser') to each, like this:
```json
{
  "clear": true,
  "view_object": {
    "users": [
      "userA", 
      "userB",
      "AnonymousUser"
    ]
  },
  "change_object": {
    "users": [
      "userB"
    ]
  },
  "delete_object": {
    "groups": [
      "admin_group"
    ]
  }
}
```

Notice that the anonymous user can only be assigned the permission of view, an existing user is required for any other permission.
