from templates.api.api_interface import APIInterface
from templates.models.exercise import Exercise
import requests
import re

API_KEY = 'AIzaSyB_ga1HNh1X3pdONl6VaxQHlgLkFnEC2fk'  # michelle's
SEARCH_ENGINE_ID = '598e742e6c308d255'

BLACKLIST = {'Axe Hold', 'Cycling', 'Upper Body', 'Upper External Oblique', 'Chin-ups', 'Wall Pushup'}
RENAME_DICT = {'Pushups': 'Chest Push-ups', 'Push Ups': 'Push-ups', 'Snach': 'Snatch',
                        "Squat Thrust": "Burpee", 'Thruster': 'Barbell Thruster Squats'}
SZ_BAR_TYPOS = {'French Press (skullcrusher) SZ-bar', 'Biceps Curls With SZ-bar', 'Upright Row, SZ-bar',
                        'Reverse Bar Curl'}
GYM_MAT_SET = {'Leg Raises, Lying', 'Side Crunch', 'Superman'}
DESCRIPTION = {
    'Dumbbell Lunges Standing': "Stand up straight with a dumbbell in each hand. Hand your arms at your sides. Palms should face the thighs (hammer grip). Feet should be a little less than shoulder-width apart. Take a big step forward with either leg, bending at the knee until the front thigh approaches parallel to the ground, landing on the heel. Inhale as you go down. The rear leg is bent at the knee and balanced on the toes. For the leg you step forward with, don't let the knee go past the tip of the toes. Step back to your standing starting position while exhaling. Repeat the motion with the other leg.",
    'Lateral Raises': "Stand or sit with a dumbbell in each hand at your sides. Keep your back straight, brace your core, and then slowly lift the weights out to the side until your arms are parallel with the floor, with the elbow slightly bent. Then lower them back down, again in measured fashion.",
    'Front Squats': "Begin with the barbell across the front side of your shoulders. Place your fingertips under the barbell just outside of your shoulders and drive your elbows up. Keeping your chest up and core tight, bend at your hips and knees to lower into a squat until your thighs are parallel to the ground. Straighten your hips and knees to drive up to the starting position."
}
GIF_MAPPER = {
    '2 Handed Kettlebell Swing': '/../static/kettlebell_gif.gif',
    'Bench Press': '/../static/bench_press_gif.gif',
    'Barbell Ab Rollout': '/../static/barbell_ab_rollout_gif.gif',
    'Barbell Lunges': '/../static/barbell_lunges_gif.gif',
    'Biceps Curls With Barbell': '/../static/biceps_curls_with_barbell_gif.gif',
    'Biceps Curls With Dumbbell': '/../static/biceps_curls_with_dumbbell_gif.gif',
    'Bench Press Narrow Grip': '/../static/bench_press_narrow_grip_gif.gif',
    'Benchpress Dumbbells': '/../static/benchpress_dumbbells_gif.gif',
    'Bent High Pulls': '/../static/bent_high_pulls_gif.gif',
    'Bentover Dumbbell Rows': '/../static/bentover_dumbbell_rows_gif.gif',
    'Bent Over Rowing': '/../static/bent_over_rowing_gif.gif',
    'Bent Over Rowing Reverse': '/../static/bent_over_rowing_reverse_gif.gif',
    'Squats': '/../static/squats_gif.gif',
    'Standing Bicep Curl': '/../static/standing_bicep_curl_gif.gif',
    'Stiff-Legged Deadlift': '/../static/stiff_legged_deadlift_gif.gif',
    'Turkish Get-Up': '/../static/turkish_getup_gif.gif',
    'Weighted Step': '/../static/weighted_step_gif.gif'
}
PLANK_REMOVED_FLAG = False

class ExerciseAPI(APIInterface, Exercise):
    @staticmethod
    def initialize_mongoDB_collection(db):
        db.exercises.drop()  # drop the old collection so we initialize a fresh collection

        exercise_counter = 0
        root_URL = 'https://wger.de/api/v2/'  # add &status=2 to only get approved exercises
        data = '{"key": "value"}'
        headers = {'Accept': 'application/json'}
        response_data = requests.get(url=root_URL, data=data, headers=headers).json()

        exercise_URL = 'https://wger.de/api/v2/exercise/?limit=224&status=2&language=2'  # english & approved exercises: total 224
        category_URL = response_data["exercisecategory"]
        muscle_URL = response_data["muscle"]
        equipment_URL = response_data["equipment"]
        image_URL = 'https://wger.de/api/v2/exerciseimage/?limit=204'
        comment_URL = 'https://wger.de/api/v2/exercisecomment/?limit=113'

        exercise_data, category_data, muscle_data, equipment_data, image_data, comment_data = ExerciseAPI.__get_json(exercise_URL,
                                                                                                    category_URL,
                                                                                                    muscle_URL,
                                                                                                    equipment_URL,
                                                                                                    image_URL,
                                                                                                    comment_URL, data,
                                                                                                    headers)
        results = exercise_data["results"]
        for x in results:
            if x["name"] and x["description"] and x["category"] and x["equipment"]:  # only exercises with complete info
                exerciseID = x["id"]

                # strip description of html elements
                description = ExerciseAPI.__clean_html(x["description"])
                if x["name"] in DESCRIPTION:  # replace bad descriptions
                    description = DESCRIPTION[x["name"]]

                # get category name using ID
                categoryID = x["category"]
                categoryResults = category_data["results"]
                category_name = ""
                for result in categoryResults:
                    if result["id"] == categoryID:
                        category_name = result["name"]
                        break

                # get muscle name using ID
                musclesList = []
                muscles = x["muscles"]
                muscleResults = muscle_data["results"]  # put this line in the get_json function
                for m in muscles:
                    for result in muscleResults:
                        if result["id"] == m:
                            musclesList.append(result["name"])  # do we want "is_front" ?
                muscles_string = ", ".join(musclesList)

                # get secondary muscle name using ID
                sec_musclesList = []
                sec_muscles = x["muscles_secondary"]
                for m2 in sec_muscles:
                    for result in muscleResults:
                        if result["id"] == m2:
                            sec_musclesList.append(result["name"])  # do we want "is_front" ?
                sec_muscles_string = ", ".join(sec_musclesList)

                # get equipment name using ID
                DEFAULT_EXERCISE_MAT_STRING = "Exercise mat"
                equipment_list = []
                equipment = x["equipment"]
                equip_results = equipment_data["results"]
                for e in equipment:
                    for result in equip_results:
                        if result["id"] == e:
                            equipmentName = result["name"]
                            equipment_list.append(equipmentName)
                if len(equipment_list) == 0:  # default equipment is Exercise mat if there is no equipment attribute returned by API
                    equipment_list.append(DEFAULT_EXERCISE_MAT_STRING)

                # get image URL using exercise
                images = []
                image_results = image_data["results"]
                query_template = "{} workout exercise"
                for result in image_results:
                    if result["exercise"] == exerciseID:
                        images.append(result["image"])
                images.extend(ExerciseAPI.__get_google_images(query_template.format(x["name"])))
                # Replace some images with gifs
                if len(images) > 0:
                    if x['name'] in GIF_MAPPER:
                        images[0] = GIF_MAPPER[x['name']]

                # get exercise comment using exercise
                comments = []
                comment_results = comment_data["results"]
                for result in comment_results:
                    if result["exercise"] == exerciseID:
                        comments.append(result["comment"])

                # Initialize subcategory variable. Use the category_name, x["name"], muscles_string, and sec_muscles_string to decide the subcategory. Note only 'Arms' and 'Legs' are broken down into subcategories
                subcategory = None
                if category_name == 'Arms':
                    subcategory = ExerciseAPI.__return_arms_subcategory(x['name'], muscles_string, sec_muscles_string)
                elif category_name == 'Legs':
                    subcategory = ExerciseAPI.__return_legs_subcategory(x['name'])

                exercise = Exercise(**{
                    "exercise_id": exerciseID, 
                    "arrayIndex": exercise_counter, 
                    "name": x["name"], 
                    "description": description, 
                    "category": category_name, 
                    "subcategory": subcategory,
                    "muscles": muscles_string,
                    "muscles_secondary": sec_muscles_string, 
                    "equipment": equipment_list,
                    "images": images, 
                    "comments": comments
                })

                if exercise.name in BLACKLIST:
                    pass
                elif ExerciseAPI.__should_add_exercise(exercise):
                    # Fix badly-named exercises
                    if exercise.name in RENAME_DICT.keys():
                        exercise.name = RENAME_DICT[exercise.name]
                    # Fix SZ-Bar/SZ-bar typos for 4 exercise name, description, and equipment attributes
                    if exercise.name in SZ_BAR_TYPOS:
                        ExerciseAPI.__fix_SZ_bar_typo(exercise)
                    # Make equipment naming consistent across all models ('Gym mat' -> 'Exercise mat')
                    if exercise.name in GYM_MAT_SET:
                        ExerciseAPI.__convert_gym_mat_to_exercise_mat(exercise)
                    db.exercises.insert_one(exercise.to_dictionary())
                    exercise_counter += 1


    # All helper methods for creating HTTP requests, cleaning, filtering, or executing APIs defined below
    # ======================================================================================================================
    @staticmethod
    def __get_json(exercise_URL, category_URL, muscle_URL, equipment_URL, image_URL, comment_URL, data, headers):
        """
        This method gets a response from all URLs needed from the wger REST API, parses it into json, and returns the json
        :return: JSON message
        """
        exercise = requests.get(url=exercise_URL, data=data, headers=headers).json()
        category = requests.get(url=category_URL, data=data, headers=headers).json()
        muscle = requests.get(url=muscle_URL, data=data, headers=headers).json()
        equipment = requests.get(url=equipment_URL, data=data, headers=headers).json()
        image = requests.get(url=image_URL, data=data, headers=headers).json()
        comment = requests.get(url=comment_URL, data=data, headers=headers).json()
        return exercise, category, muscle, equipment, image, comment


    @staticmethod
    def __should_add_exercise(exercise):
        """
        Helper function called in the initialize_mongoDB_exercises_collection() method to mark specific exercise duplicates
        that should NOT be added to the database. These can't be eliminated with the simple blacklist due to identical exercise names.
        This method achieves the following rules:
        1.) Blacklists one of the 'Military Press' exercise with Category == Arms
        2.) Blacklists the first of 2 'Plank' exercises using the global PLANK_REMOVED_FLAG
        3.) Blacklist spanish exercise 'Curl su Panca a 45°" using substring.
        :param exercise: an Exercise object that should have all attributes initialized
        :return: Boolean, True if exercise should be added, False otherwise
        """

        if exercise.name == 'Military Press' and exercise.category == 'Arms':
            return False
        elif exercise.name == 'Plank' and PLANK_REMOVED_FLAG is False:
            return False
        elif 'Curl su Panca a ' in exercise.name:
            return False
        else:
            return True


    @staticmethod
    def __fix_SZ_bar_typo(exercise):
        """
        Helper function to fix the SZ-Bar and SZ-bar typos for 4 equipment names, descriptions, and equipment attributes.
        :param exercise: Exercise object with name verified to be in the SZ_BAR_TYPO set
        :return: None
        """
        exercise.name = exercise.name.replace('SZ-Bar', 'EZ-Bar')
        exercise.name = exercise.name.replace('SZ-bar', 'EZ-bar')
        exercise.description = exercise.description.replace('SZ-Bar', 'EZ-Bar')
        exercise.description = exercise.description.replace('SZ-bar', 'EZ-bar')
        new_equipment_list = []
        for e in exercise.equipment:
            if e == 'SZ-Bar':
                new_equipment_list.append('EZ-Bar')
            else:
                new_equipment_list.append(e)
        exercise.equipment = new_equipment_list


    @staticmethod
    def __convert_gym_mat_to_exercise_mat(exercise):
        """
        Helper function that renames the equipment attribute for 3 exercises from 'equipment = Gym mat' to 'equipment = Exercise mat'.
        To have consistent tags and link instances across models, we need consistent names.
        :param exercise: An exercise object from the GYM_MAT_SET
        :return: None
        """
        exercise.equipment = ['Exercise mat']


    @staticmethod
    def __return_arms_subcategory(exerciseName, muscles_string, sec_muscles_string):
        if 'Bicep' in exerciseName:
            return 'Bicep'
        elif 'Tricep' in exerciseName:
            return 'Tricep'
        else:
            if 'Biceps' in muscles_string:
                return 'Bicep'
            elif 'Triceps' in muscles_string:
                return 'Tricep'
            else:
                if 'Biceps' in sec_muscles_string:
                    return 'Bicep'
                elif 'Triceps' in sec_muscles_string:
                    return 'Tricep'
                else:  # If exercise fits neither subcategory, return None
                    return None


    @staticmethod
    def __return_legs_subcategory(exerciseName):
        if 'Squat' in exerciseName:
            return 'Squats'
        elif 'Deadlift' in exerciseName:
            return 'Deadlift'
        else:  # There are 5 specific exercises that don't fall under Squats or Deadlift subcategory... check <https://github.com/UT-SWLab/TeamA13/issues/47> for more details
            return None


    @staticmethod
    def __clean_html(raw_html):
        """
        This method takes a raw HTML string and returns a string without the HTML elements
        """
        clean = re.compile('<.*?>')
        clean_text = re.sub(clean, '', raw_html)
        return clean_text


    @staticmethod
    def __get_google_images(search_string, file_type=None):
        """
        This method makes a request to the Google Custom Search API and returns the 10 images in the search result as a
        list of strings, where each string represents an image URL. Can pass in additional optional params
        :param search_string: query string that will be searched
        :param file_type: Optional file-type parameter to limit resulting extension types in the result
        :return: List of image URLs
        """
        if file_type is not None:
            url = f"https://customsearch.googleapis.com/customsearch/v1?searchType=image&key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_string}&fileType={file_type}"
        else:
            url = f"https://customsearch.googleapis.com/customsearch/v1?searchType=image&key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_string}"
        data = requests.get(url).json()
        search_items = data.get("items")
        images = []
        if search_items:
            for item in search_items:
                image_link = item["link"]
                if ExerciseAPI.__imageURL_exists(image_link):
                    images.append(image_link)
        return images


    @staticmethod
    def __imageURL_exists(path):
        try:
            r = requests.head(path)
            return r.status_code == requests.codes.ok
        except:
            return False
