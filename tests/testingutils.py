import unittest
from flask.json import loads

from server import usermanager
import gris

class ApplicationTestBase(unittest.TestCase):
    def setUp(self):
        gris.app.config["TESTING"] = True
        self.app = gris.app.test_client()
        self.result = None

    def tearDown(self):
        # usermanager.logout()
        pass

    def get(self, *args, **kwargs):
        self.result = self.app.get(*args, **kwargs)
        return self.result.get_data()

    def get_json(self, *args, **kwargs):
        return loads(self.get(*args, **kwargs))

    def post(self, *args, **kwargs):
        self.result = self.app.post(*args, **kwargs)
        return self.result.get_data()

    def post_json(self, *args, **kwargs):
        return loads(self.post(*args, **kwargs))

    def assertAborted(self, code, message=None):
        self.assertEqual(self.result.status_code, code)
        data = loads(self.result.get_data())
        self.assertEqual(data["code"], code)
        self.assertEqual(data["message"], message)

    def assertSuccessful(self):
        self.assertEqual(self.result.status, "200 OK")

    def assertSuccess(self, message=None):
        self.assertEqual(self.result.status, "200 OK")
        data = loads(self.result.get_data())
        self.assertEqual(data["success"], True)
        if message is not None:
            self.assertEqual(data["message"], message)
