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

    def test_delete_question(self):
        # create a question and then delete
        # you can call the create endpoint but we are unittesting
        # so just create with backend, reason below
        # (do not want to use one endpoint(create) to test another(delete))
        question = Question(question="testQuestionDelete", 
                            answer="testAnswerDelete", 
                            category=1,
                            difficulty=1)
        # insert
        question.insert()
        id = question.id
            
        # add a clean up incase the test fails
        def clean_up():
            questions = Question.query.filter(Question.question == "testQuestionDelete").all()
            for question in questions:
                question.delete()
        self.addCleanup(clean_up)
            
        # retrieve
        q = Question.query.filter(Question.question == "testQuestionDelete").first()
        print (q.format())
        self.assertEqual(q.question,"testQuestionDelete")
        self.assertEqual(q.answer, "testAnswerDelete")

        res = self.client().delete("/questions/"+str(id))
        self.assertEqual(res.status_code, 200)

        print(res.data)
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)
        self.assertEqual(len(Question.query.filter(Question.question == "testQuestionDelete").all()), 0)

        
        #negative
        res = self.client().delete("/questions/"+str(0))
        self.assertEqual(res.status_code, 422)

    def test_add_question(self):
        # add a clean up incase the test fails
        def clean_up():
            questions = Question.query.filter(Question.question == "testQuestionAdd").all()
            for question in questions:
                question.delete()
        self.addCleanup(clean_up)
        # insert
        res = self.client().post("/questions",
                                data=json.dumps({
                                    "question": "testQuestionAdd",
                                    "answer": "testAnswerAdd",
                                    "difficulty": 4,
                                    "category": 1
                                 }),
                                 content_type="application/json")
        self.assertEqual(res.status_code, 200)

        print(res.data)
        data = json.loads(res.data)
        #verify response data
        self.assertEqual(data["success"], True)
           
        # retrieve
        q = Question.query.filter(Question.question == "testQuestionAdd").first()
        print (q.format())
        self.assertEqual(q.question,"testQuestionAdd")
        self.assertEqual(q.answer, "testAnswerAdd")
        self.assertEqual(q.difficulty, 4)
        self.assertEqual(q.category, 1)


        #negative if bad json data
        #negative test 1
        # 400 if bad body
        res = self.client().post("/questions",                                 
                                 content_type="application/json")
        self.assertEqual(res.status_code, 400)
        
        data = json.loads(res.data)
        self.assertEqual(data["message"],"Bad request")


    def test_search_question(self):
        # postive search
        question = Question(question="testQuestionSearch", 
                            answer="testAnswerSearch", 
                            category=1,
                            difficulty=1)
        # insert
        question.insert()
        id = question.id
            
        # add a clean up incase the test fails
        def clean_up():
            questions = Question.query.filter(Question.question == "testQuestionSearch").all()
            for question in questions:
                question.delete()
        self.addCleanup(clean_up)

        res = self.client().post("/questionsearch",
                                data=json.dumps({
                                    "searchTerm": "questionSearch"
                                 }),
                                 content_type="application/json")
        
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertEqual(data["totalQuestions"], 1)
        self.assertEqual(data["questions"][0]["answer"], "testAnswerSearch")
    

        #negative test 1
        # 400 if bad body
        res = self.client().post("/questionsearch",                                 
                                 content_type="application/json")
        self.assertEqual(res.status_code, 400)
        
        data = json.loads(res.data)
        self.assertEqual(data["message"],"Bad request")

        #negative if not found
        # 404
        res = self.client().post("/questionsearch",
                                data=json.dumps({
                                    "searchTerm": "notaquestion"
                                 }),
                                 content_type="application/json")
        self.assertEqual(res.status_code, 404)
        
        data = json.loads(res.data)
        self.assertEqual(data["message"],"Not Found")

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
    
    def test_quizzes(self):
        pass

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()