import json
import urllib.parse
from typing import Type
from unicodedata import name
from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, Group, Permission
from django.contrib.auth.models import User
from django.test.client import Client
from django.contrib.contenttypes.models import ContentType

from nosql_objects.models import ObjectClass


class ObjectsTestCase(TestCase):
    userA: AbstractBaseUser
    userAClient: Client
    userB: AbstractBaseUser
    userBClient: Client
    userC: AbstractBaseUser
    userCClient: Client
    userGroupA: Group
    userAdmin: AbstractBaseUser
    objectClassA: ObjectClass
    objectClassB: ObjectClass
    userAnon: Client
    

    def setUp(self):
        # General setup
        userModel = User.objects
        
        # Create object groups
        object_contentType = ContentType.objects.get(
            app_label="baas_objects", model="object"
        )
        objectClass_contentType = ContentType.objects.get(
            app_label="baas_objects", model="objectclass"
        )
        access_objects_group = Group.objects.create(name="objects")
        user_subgroup = Group.objects.create(name="user_subgroup")

        # Admin user
        self.userAdmin = userModel.create_superuser( "userAdmin", "userAdmin@test.com", "testingA")

        # Permissions (assign add permission to testing users)
        object_perms = Permission.objects.filter(content_type=object_contentType)
        for perm in object_perms:
            access_objects_group.permissions.add(perm)
        access_objects_group.save()

        # Users in tests
        self.userA = userModel.create_user("userA", "userA@test.com", "testing_userA")
        self.userA.groups.add(access_objects_group)
        self.userAClient = Client()
        self.userAClient.login(username=self.userA.username, password="testing_userA")
        self.userB = userModel.create_user("userB", "userB@test.com", "testing_userB")
        self.userB.groups.add(access_objects_group)
        self.userBClient = Client()
        self.userBClient.login(username=self.userB.username, password="testing_userB")
        self.userC = userModel.create_user("userC", "userC@test.com", "testing_userC")
        self.userC.groups.add(access_objects_group)
        self.userC.groups.add(user_subgroup)
        self.userCClient = Client()
        self.userCClient.login(username=self.userC.username, password="testing_userC")
        self.userAnon = Client()

        # Object classes
        self.objectClassA = ObjectClass(name="classA", created_by=self.userAdmin, updated_by=self.userAdmin)
        self.objectClassA.save()
        self.objectClassB = ObjectClass(name="classB", created_by=self.userAdmin, updated_by=self.userAdmin)
        self.objectClassB.save()

    def test_user_can_create_and_read_object(self):
        object = self.crete_obj({"value1": 1, "value2:": "otherValue"})        

        id = str(object['id'])
        request = self.userAClient.get("/api/objects/"+id+"/", object, content_type="application/json")
        self.assertEqual(request.status_code, 200, "Get object")
       
    def test_user_can_update_object(self):
        object1 = self.crete_obj({"value1": 1, "value2:": "otherValue"})   
        version1 = object1['version']
        id = str(object1['id'])
        object2 = object1
        object2['data'] = {"value1": 1, "value2:": "otherValue", "value3": "newValue"}
        request = self.userAClient.patch("/api/objects/"+id+"/", object1, content_type="application/json")
        self.assertEqual(request.status_code, 200, "post object change")
        version2 = request.data['version']
        self.assertNotEqual(version1, version2, "Version changed")
        self.assertEqual(request.data['data']['value3'], "newValue", "Value added to object")

    def test_user_can_only_list_and_update_its_own_objects(self):
        objectA = self.crete_obj({"user":"A"}, client=self.userAClient)
        objectB = self.crete_obj({"user":"B"}, client=self.userBClient)
        requestA = self.userAClient.get("/api/objects/", content_type="application/json")
        requestB = self.userBClient.get("/api/objects/", content_type="application/json")
        requestAErrorGet = self.userAClient.get("/api/objects/"+str(objectB['id'])+'/', content_type="application/json")
        requestAErrorPost = self.userAClient.post("/api/objects/"+str(objectB['id'])+'/', objectB, content_type="application/json")
        requestAErrorPatch = self.userAClient.patch("/api/objects/"+str(objectB['id'])+'/', objectB, content_type="application/json")

        self.assertEqual(requestA.data['count'], 1, "count number of objects with permission for user A")
        self.assertEqual(requestA.data['results'][0]['created_by'], self.userA.pk, "User A created object")
        self.assertEqual(requestB.data['count'], 1, "count number of objects with permission for user B")
        self.assertEqual(requestB.data['results'][0]['created_by'], self.userB.pk, "User B created object")
        self.assertNotEqual(requestA.data['results'][0]['created_by'], requestB.data['results'][0]['created_by'], "User different in object updates")
        self.assertEqual(requestAErrorGet.status_code, 404, "object should not be visible")
        self.assertEqual(requestAErrorPost.status_code, 405, "change should not be allowed without permission")
        self.assertEqual(requestAErrorPatch.status_code, 404, "changed object should not be visible")

    def test_object_perms(self):
        # create objects
        objectA = self.crete_obj({"user":"A"}, client=self.userAClient)
        objectB = self.crete_obj({"user":"B"}, client=self.userBClient)
        
        # test object is private
        request = self.userBClient.get("/api/objects/"+str(objectA["id"])+"/", content_type="application/json")
        self.assertEqual(request.status_code, 404, "not getting object without permissions")
        
        # set permission on object
        perms = {
            "view_object": {
                "users": [self.userB.get_username()],
                "groups": ["user_subgroup"]
            }
        }        
        request = self.userAClient.post("/api/objects/"+str(objectA["id"])+"/perms/", perms, content_type="application/json")        
        self.assertEqual(request.status_code, 200, "add object perms")
        
        # test object perms endpoint is private
        request = self.userAClient.post("/api/objects/"+str(objectB["id"])+"/perms/", perms, content_type="application/json")
        self.assertEqual(request.status_code, 403, "not be able to change perms on not owned object")
        
        # test shared object with other user
        request = self.userBClient.get("/api/objects/"+str(objectA["id"])+"/", content_type="application/json")
        self.assertEqual(request.status_code, 200, "get shared object with user permission")
        self.assertEqual(request.data['data']['user'], "A", "check shared object")
        
        # test shared object with group
        request = self.userCClient.get("/api/objects/"+str(objectA["id"])+"/", content_type="application/json")
        self.assertEqual(request.status_code, 200, "get shared object with group permission")
        self.assertEqual(request.data['data']['user'], "A", "check shared object")

        # remove permissions
        perms = {
            "clear": True,
            "groups": ["user_subgroup"]
        }        
        request = self.userAClient.post("/api/objects/"+str(objectA["id"])+"/perms/", perms, content_type="application/json")        
        self.assertEqual(request.status_code, 200, "add object perms")

        # permission should be lost!
        request = self.userAClient.get("/api/objects/"+str(objectA["id"])+"/", content_type="application/json")
        self.assertEqual(request.status_code, 404, "not getting object after losing perms")

        # test shared object with group after clearing
        request = self.userCClient.get("/api/objects/"+str(objectA["id"])+"/", content_type="application/json")
        self.assertEqual(request.status_code, 200, "get shared object with group permission")

    def test_list_objects_by_class(self):
        objectA = self.crete_obj({"user":"A"}, className="classA", client=self.userAClient)
        objectB = self.crete_obj({"user":"B"}, className="classB", client=self.userAClient)
        
        request = self.userAClient.get("/api/objects/?object_class=classA", content_type="application/json")
        self.assertEqual(request.data['count'], 1, "count number of objects on class A filtering by name")
        self.assertEqual(request.data['results'][0]['created_by'], self.userA.pk, "User A created object")

        request = self.userAClient.get("/api/objects/?object_class="+str(self.objectClassA.pk), content_type="application/json")
        self.assertEqual(request.data['count'], 1, "number of objects on class A filtering by pk")
        self.assertEqual(request.data['results'][0]['created_by'], self.userA.pk, "User A created object")

    def test_querying_data(self):
        # https://docs.djangoproject.com/en/3.1/topics/db/queries/#querying-jsonfield
        objectA = self.crete_obj({"my_data":"A"}, className="classA", client=self.userAClient)

        query_params = self.create_queryParams({'my_data':'A'})
        request = self.userAClient.get("/api/objects/?query="+query_params, content_type="application/json")
        self.assertEqual(request.data['results'][0]['id'], objectA['id'], "object found with query")

        query_params = self.create_queryParams({'my_data':'B'})
        request = self.userAClient.get("/api/objects/?query="+query_params, content_type="application/json")
        self.assertEqual(request.data['count'], 0, "number of objects on not existing data")

    def test_anonymous_objects(self):
        objectA = self.crete_obj({"user":"A"}, client=self.userAClient)

        request = self.userAClient.get("/api/objects/", content_type="application/json")        
        self.assertEqual(request.data['count'], 1, "one objects visible to signed user")

        request = self.userAnon.get("/api/objects/", content_type="application/json")        
        self.assertEqual(request.data['count'], 0, "no objects visible to anonymous user")

        objectAnon = {"object_class": "classA", "data": {}}
        request = self.userAnon.post("/api/objects/", objectAnon, content_type="application/json")
        self.assertEqual(request.status_code, 401, "no object creation for anonymous user")

        request = self.userAnon.patch("/api/objects/"+str(objectA['id'])+"/", objectAnon, content_type="application/json")
        self.assertEqual(request.status_code, 401, "no object update for anonymous user")
        
        perms = {
            "view_object": {
                "users": ['AnonymousUser']
            }
        }
        request = self.userAClient.post("/api/objects/"+str(objectA["id"])+"/perms/", perms, content_type="application/json")        
        self.assertEqual(request.status_code, 200, "add object perms to anonymous user")

        request = self.userAnon.get("/api/objects/"+str(objectA["id"])+"/", content_type="application/json")    
        self.assertEqual(request.status_code, 200, "get object")    
        self.assertEqual(request.data['id'], objectA['id'], "object found with annon user")

        request = self.userAnon.get("/api/objects/", content_type="application/json")        
        self.assertEqual(request.data['count'], 1, "number of objects found with annon user")

    def crete_obj(self, data, className = None, client = None) -> dict:
        if not className: className = "classA"
        if not client: client = self.userAClient
        object1 = {"object_class": className, "data": data}
        request = client.post("/api/objects/", object1, content_type="application/json")
        self.assertEqual(request.status_code, 201, "Create new object")
        return request.data

    def create_queryParams(self, params: dict) -> str:
        return urllib.parse.quote(json.dumps(params))
