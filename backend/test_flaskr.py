import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia" #Set Database here
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        self.assertEqual(res.status_code, 200)
        
        data = json.loads(res.data)
        self.assertIsNotNone(data["categories"])
        self.assertEqual(data["categories"]["1"], "Science")

    def test_get_questions(self):
        # positive test
        res = self.client().get("/questions?page=1")
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue(data["totalQuestions"]<=10)

        #assumes atleast one question exists
        self.assertTrue("questions" in data)
        self.assertTrue(data["questions"])

        keys = ["question", "answer", "category"]

        for key in keys:
            self.assertTrue(key in data["questions"][0])
            self.assertIsNotNone(data["questions"][0][key])

        #negative, search for key
        self.assertFalse("hint" in data["questions"][0])

        #negative, error
        res = self.client().get("/questions?page=-1")
        self.assertEqual(res.status_code, 422)

    def test_get_questions_by_category(self):
        # positive test
        res = self.client().get("/categories/1/questions")
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue(data["currentCategory"], "Science")

        #assumes atleast one question exists
        self.assertTrue("questions" in data)
        self.assertTrue(data["questions"])

        keys = ["question", "answer", "category"]

        for key in keys:
            self.assertTrue(key in data["questions"][0])
            self.assertIsNotNone(data["questions"][0][key])

        #negative, search for key
        self.assertFalse("hint" in data["questions"][0])

        #negative, error
        res = self.client().get("/categories/0/questions")
        self.assertEqual(res.status_code, 422)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()