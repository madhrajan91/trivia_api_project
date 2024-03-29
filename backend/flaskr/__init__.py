import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-METHODS', 'GET,PATCH,POST,DELETE,OPTIONS')
    #print (response.headers)
    return response
  

  @app.route('/')
  @cross_origin()
  def index():
    return jsonify(name = "Index",
                   message = 'This is a homepage message')

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.all()
    result = {}
    for c in categories:
      #result.append(c.format())
      result[c.id] = c.type
    return jsonify({
        "categories": result
      })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    if page < 1:
      abort(422)

    page_size = 10
    questions = Question.query.filter().limit(page_size).offset((page-1)*page_size).all()

    questionsResult = []
    categoryMap = {}
    for question in questions:
      questionsResult.append(question.format())
      if question.category not in categoryMap:
        categoryMap[question.category] = question.category_rec.type
    
    categories = Category.query.all()
    result = {}
    for c in categories:
      result[c.id] = c.type

    return jsonify({
      "totalQuestions": len(questionsResult),
      "questions":questionsResult,
      "categories": result, # this does not make sense for a list of questions but the react-app asked for it
      "currentCategory": "-" # same as above, this is not applicable if we retrieve a list of questions
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_questions(question_id):
    error = False
    
    try:
      question = Question.query.filter(Question.id == question_id).first()
      #print (question.format())
      if question is None:
        error = True
      else:
        question.delete()

    except:
      error = True
      Question.rollback()
    finally:
      Question.close()
      # do not want to publish a 500 message
      # return 422 here
      if error:
        abort(422)
    
    return jsonify({
        "success": True
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    print("add question")
    data = request.get_json()
    question = Question(question=data["question"],
                          answer=data["answer"],
                          category=data["category"],
                          difficulty=data["difficulty"])
    try:
      question.insert()

    except:
      question.rollback()
      abort(404)
    finally:
      question.close()
    
    return jsonify({
      "success": True
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  #https://stackoverflow.com/questions/5020704/how-to-design-restful-search-filtering
  @app.route('/questionsearch', methods=['POST'])
  def search_question():

    data = request.get_json()

    if data is None or "searchTerm" not in data:
      abort(404)
    
    searchTerm = data["searchTerm"]
    print(searchTerm)
    questions = Question.query.filter(Question.question.ilike('%'+searchTerm+'%')).all()

    if (len(questions)>0):
      questionResults = []
      for question in questions:
        questionResults.append(question.format())

      return jsonify({
        "totalQuestions": len(questionResults),
        "questions": questionResults,
        "currentCategory": '-' # does not make sense
      })
    else:
      abort(404)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route("/categories/<category_id>/questions", methods=['GET'])
  def get_questions_by_categories(category_id):
    error = False
    try:
      category = Category.query.filter(Category.id==category_id).first()

      questionResults = []
      for question in category.questions:
        questionResults.append(question.format())

    except:
      error = True
    finally:
      # do not want to publish a 500 message
      # return 422 here
        if error:
          abort(422)

    return jsonify({
      "totalQuestions": len(questionResults),
      "questions": questionResults,
      "currentCategory": category.type
    })
      
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz():
    data = request.get_json()
    
    previous_questions = []
    questions = []

    if "previous_questions" in data:
      previous_questions = data["previous_questions"]

    if "quiz_category" in data:
      quiz_category = data["quiz_category"]
      category = Category.query.get(quiz_category['id'])
      questions = category.questions
    
    else:
      questions = Question.query.all()

    print(previous_questions)
    filteredQuestions = []
    if len(previous_questions)>0:
      for question in questions:
        if question.id not in previous_questions:
          filteredQuestions.append(question)
    else:
      filteredQuestions = questions

    result = {}
    if len(filteredQuestions) > 0:
      result = {
        "question" : filteredQuestions[random.randint(0, len(filteredQuestions)-1)].format()
      }


    return jsonify(result)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  # Implementing one error handler for 404 and one error handler for 422
  # I could put both in one handler instead

  @app.errorhandler(400)
  def unprocessable_entity(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "Bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Not Found"
    }), 404

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "Unprocessable entity"
    }), 422
  
  return app

    