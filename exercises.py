from flask import Flask, render_template, request
import json
import requests
from pprint import pprint

app = Flask(__name__)

class Exercise:
    def __init__(self, name, description, category, muscles, muscles_secondary, equipment, images, comments):
        self.name = name
        self.description = description
        self.category = category
        self.muscles = muscles
        self.muscles_secondary = muscles_secondary
        self.equipment = equipment
        self.images = images
        self.comments = comments


def get_exercises():
    exerciseArray = []

    root_URL = 'https://wger.de/api/v2/' # add &status=2 to only get approved exercises 
    data = '{"key": "value"}'
    headers = {'Accept': 'application/json'}
    response = requests.get(url=root_URL, data=data, headers=headers)
    response_data = response.json()

    # exercise_URL = response_data["exercise"]
    # exercise_URL = 'https://wger.de/api/v2/exercise/?limit=100'
    exercise_URL = 'https://wger.de/api/v2/exercise/?limit=224&status=2&language=2' # english, approved exercises: total 224 
    category_URL = response_data["exercisecategory"]
    muscle_URL = response_data["muscle"]
    equipment_URL = response_data["equipment"]
    # image_URL = response_data["exerciseimage"]
    image_URL = 'https://wger.de/api/v2/exerciseimage/?limit=204'
    # comment_URL = response_data["exercisecomment"]
    comment_URL = 'https://wger.de/api/v2/exercisecomment/?limit=113'

    exercise_data = get_json(exercise_URL, data, headers)
    category_data = get_json(category_URL, data, headers)
    muscle_data = get_json(muscle_URL, data, headers)
    equipment_data = get_json(equipment_URL, data, headers)
    image_data = get_json(image_URL, data, headers)
    comment_data = get_json(comment_URL, data, headers)

    nextURL = exercise_data["next"]
    results = exercise_data["results"]
    for x in results:
        exerciseID = x["id"]

        # get category name using ID
        categoryID = x["category"]
        categoryResults = category_data["results"]
        categoryName = ""
        for result in categoryResults:
            if result["id"] == categoryID:    
                categoryName = result["name"]
                break

        # get muscle name using ID
        musclesList = []
        muscles = x["muscles"]
        muscleResults = muscle_data["results"]  # put this line in the get_json function
        for m in muscles:
            for result in muscleResults:
                if result["id"] == m:
                    musclesList.append(result["name"])  # do we want "is_front" ?
            
        # get secondary muscle name using ID    
        sec_musclesList = []
        sec_muscles = x["muscles_secondary"]
        for m2 in sec_muscles:
            for result in muscleResults:
                if result["id"] == m2:
                    sec_musclesList.append(result["name"])  # do we want "is_front" ?
            
        # get equipment name using ID
        equipment_list = []
        equipment = x["equipment"]
        equip_results = equipment_data["results"]
        for e in equipment:
            for result in equip_results:
                if result["id"] == e:
                    equipment_list.append(result["name"])

        # get image URL using exercise # (if exists) -----> need to go through all exercise images list *********
        images = []    # list of image URLs --------> save image in db instead of going to website?
        image_results = image_data["results"]
        for result in image_results:
            if result["exercise"] == exerciseID:
                images.append(result["image"])

        # get exercise comment using exercise # (if exists)
        comments = []    # list of image URLs --------> save image in db instead of going to website?
        comment_results = comment_data["results"]
        for result in comment_results:
            if result["exercise"] == exerciseID:
                comments.append(result["comment"])

        exercise = Exercise(x["name"], x["description"], categoryName, musclesList, sec_musclesList, equipment_list, images, comments)
        exerciseArray.append(exercise)
        pprint(exercise)
    return exerciseArray

def get_json(url, data, headers):
    response = requests.get(url=url, data=data, headers=headers)
    return response.json()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/exercises', methods=['GET'])
def exercises():
    exercisesArray = get_exercises()
    return render_template('exercises.html', exercisesArray = exercisesArray)    

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')    


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)