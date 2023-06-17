import json

from flask import Flask, Response, jsonify, redirect, request
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient('mongodb://localhost:27017')


db = client['InfoSys']
coll= db['Courses']
app = Flask(__name__)

# Insert a course 
@app.route('/insert-course', methods=['POST'])
def insert_course():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data or not "course_id" in data or not "ects" in data or not "email":
        return Response("Information incompleted",status=500,mimetype="application/json")
    
    if coll.find({"course_id":data["course_id"]}).count() == 0 :
        course = {"course_id": data['course_id'], "name": data['name'],  "ects":data['ects'], "email":data['email'] }
        # Add student to the 'students' collection
        coll.insert_one(course)
        return Response("Course : "+data['name']+" was added to the Mongo Database",status=200,mimetype='application/json') 
    else:    #In case of a duplicate course_id data does not append to the "Courses" collection
        return Response("A course with the given "+data['course_id']+" already exists",status=200,mimetype='application/json')



# Find the requested course id and complete info of it
@app.route('/get-course', methods=['GET'])
def get_Course():
    course_id = request.args.get('course_id')
    if course_id == None :
            return Response("Bad request", status=500, mimetype='application/json')
    course = coll.find_one({"course_id":course_id})
    if course !=None : 
             course = {'name':course["name"],'ects':course["ects"], 'course_id':course["course_id"] }
             return jsonify(course)
    return Response('No course found with that id: ' + course_id + ' was found' ,status=500,mimetype='application/json')



# Find course and add a description to it with POST method
@app.route('/insert-course-description', methods=['POST'])
def insert_course_description():
    course_id = request.args.get('course_id')
    if course_id == None: 
             return Response("Bad request", status=500, mimetype='application/json')
    course = coll.find_one({"course_id":course_id})
    if course == None :
             return Response("No course found with that course_id : "+course_id,status=500,mimetype='application/json')
    try:
             course = coll.update_one({"course_id":course_id},
             {"$set":
             {  
                 "description": request.form["description"]
             }
             })
             return Response({'Description added successfuly'},status=200,mimetype='application/json')
    except Exception as e:
             return Response({'Course could not be updated'},status=500,mimetype='application/json')            



# Add course_id to an existing course
@app.route('/add-course/<string:email>', methods=['PUT'])
def add_course(email):
    if email == None : 
             return Response("Bad request", status=500, mimetype='application/json')
    course = coll.find_one({"email":email})
    if course == None:
             return Response({'No student with such email : '+email+' was found '},status=500,mimetype='application/json')
    try : 
             course = coll.update_one({"email":email},
             {"$set":
                {    
                  "course_id": request.form["course_id"]
                }  
             })
             return Response({'Course_id was added successfuly'},status=200,mimetype='application/json')
    except Exception as e:
             return Response({'Course_id could not be updated'},status=500,mimetype='application/json')



# Find student by email and remove-delete
@app.route('/delete-student', methods=['DELETE'])
def delete_student():
    email = request.args.get('email')
    if email == None : 
              return Response("Bad request", status=500, mimetype='application/json')
    course = coll.find_one({"email" : email})
    if course != None :
              coll.delete_one({"email": email})
              return Response("Student was successfuly removed ",status=200,mimetype='application/json')

    return Response("Student couldn't be found and therefore not be deleted",status=500,mimetype='application/json')


# Find course by course_id and update its information with put method
@app.route('/update-course', methods=['PUT'])
def update_course():
    course_id = request.args.get('course_id')
    if course_id == None:
             return Response({"Bad request"}, status=500, mimetype='application/json')
    course = coll.find_one({"course_id" : course_id })
    if course == None : 
             return Response('No course found with the following id : ' +course_id, status = 500 , mimetype='application/json')
    
    try:
             course = coll.update_one({"course_id":course_id},
             {"$set":
             {
                 "course_id": request.form["course_id"],
                 "name": request.form["name"],
                 "ects": int(request.form["ects"]),
                 "description": request.form["description"]
             }
             })
             return Response({'Course updated successfuly'},status=200,mimetype='application.json')
    except Exception as e:
             return Response({'Course could not be updated'}, status=500, mimetype='application/json')

                
# Run flask service
if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5000)
