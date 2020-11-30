from templates.models.equipment import Equipment
from ebaysdk.finding import Connection

BLACKLIST = {'NEW CAP Barbell Standard Barbell Weight Lifting Exercise Bar 5 foot ft - NEW',
             'NOS BMX Freestyle SKYWAY EZ Bar handlebar decals',
             'BUKA GEARS ARNOLD WEIGHT LIFTING BODYBUILDING BICEP ARM BLASTER EZ BAR CURL ARMS',
             '9HORN Exercise Mat/Protective Flooring Mats with EVA Foam Interlocking Tiles and',
             'HOMELITE SUPER-EZ Bar Guides Inner/Outer Used',
             'Chauvet DJ EZ Bar EZBAR Battery Powered Light Bars Pair w EZ Pin Spotlight Pack',
             'Chauvet DJ EZ Bar Battery-Powered Pin Spot Light Bars with Carry Case',
             'Chauvet DJ EZ Bar EZBAR Battery Powered Light Bar w 3 Independent Pin Spots',
             'Chauvet DJ EZ Bar Battery-Powered Pin Spot Light Bar with Carry Case',
             'CHAUVET DJ EZBar EZ Bar 3 Pin Spot Battery-Powered Bar Light PROAUDIOSTAR'
             }
IMAGE_MAPPER = {
    'Cast Iron Kettlebell 5, 10, 15, 20, 25, 30 35,40,45 50+some PAIRS(Choose Weight': "kettlebell_picture_1.jpg",
    'POWERT Cast Iron Kettlebell Weight Lifting 10-50LB': "kettlebell_picture_2.jpg",
    'POWERT Vinyl Coated Kettlebell for Weight Lifting Workout 5-50LB--Single': "kettlebell_picture_3.jpg",
    'NEW FRAY FITNESS RUBBER HEX DUMBBELLS select-weight 10,15, 20, 25, 30, 35, 40LB': "dumbbell_picture_1.jpg",
    'New Dumbbell Dumbbells from 5-25 Lbs Rubber Coated Hex Sold by pairs': "dumbbell_picture_2.jpg",
    'FLYBIRD Adjustable Weight Bench Incline Decline Foldable Workout Gym Exercise': 'bench_picture_1.png',
    'Yoga Mats 0.375 inch (10mm) Thick Exercise Gym Mat Non Slip With Carry Straps': "mat_picture_1.png",
    'Extra Thick Non-slip Yoga Mat Pad Exercise Fitness Pilates w/ Strap 72" x 24"': "mat_picture_2.jpg",
    'Thick Yoga Mat Gym Camping Non-Slip Fitness Exercise Pilates Meditation Pad US': "mat_picture_3.jpg",
    'Exercise Yoga Mat Thick Fitness Meditation Camping Workout Pad or Carrier Strap': "mat_picture_4.jpg",
    '72" x 24" Exercise Yoga Mat 1/2" Thick w/ Carry Strap - Pilates Fitness': "mat_picture_5.jpg"
}
ID_SET = set()


class EquipmentAPI:
    @staticmethod
    def initialize_mongoDB_collection(db):
        db.equipments.drop()  # drop the old collection so we initialize a fresh collection
        equipment_counter = 0
        EBAY_APP_ID = "AndrewWu-IMBDProj-PRD-be64e9f22-1cd7edca"  # Andrew's App ID
        api = Connection(appid=EBAY_APP_ID, config_file=None)
        queryArray = ['Kettlebell', 'Dumbbell', 'Barbell', 'Bench', 'EZ-Bar', 'Exercise mat', 'Pull-up bar']
        queryMapper = {'Kettlebell': 'Kettlebells'}

        for query in queryArray:
            queryTermSaved = query
            if query in queryMapper.keys():
                query = queryMapper[query]
            api_result = api.execute('findItemsAdvanced', {
                'keywords': [query],
                'paginationInput': {
                    'entriesPerPage': '12',
                    'pageNumber': '1'
                }})
            api_result_dict = api_result.dict()
            shopping_results_arr = api_result_dict["searchResult"]["item"]

            for result in shopping_results_arr:
                # May need to add more vars and checks later
                galleryURL = None
                # if 'galleryPlusPictureURL' in result:
                #     galleryURL = result['galleryPlusPictureURL']
                # else:
                if 'galleryURL' in result:
                    galleryURL = result['galleryURL']

                if galleryURL is not None:
                    # Mark broken images that need to be loaded statically
                    replacePictureFlag = False
                    if result['title'] in IMAGE_MAPPER:
                        replacePictureFlag = True

                    eq = Equipment(**{
                        "itemId": result['itemId'],
                        "arrayIndex": equipment_counter,
                        "title": result['title'],
                        "value": float(result['sellingStatus']['convertedCurrentPrice']['value']),
                        "categoryName": result['primaryCategory']['categoryName'],
                        "location": result['location'],
                        "replacePictureFlag": replacePictureFlag,
                        "galleryURL": galleryURL,
                        "viewItemURL": result['viewItemURL'],
                        "equipmentCategory": queryTermSaved
                    })
                    # Rewrite bad picture URL with picture's filename
                    if eq.replacePictureFlag is True:
                        eq.picture = IMAGE_MAPPER[eq.name]

                    # Skip equipment entries that are known to have bad titles/images
                    if eq.name in BLACKLIST:
                        pass
                    # avoid adding duplicate items to our database
                    elif eq.id not in ID_SET:
                        db.equipments.insert_one(eq.to_dictionary())
                        ID_SET.add(eq.id)
                        equipment_counter += 1
