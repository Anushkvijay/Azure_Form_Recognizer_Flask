#config file to save endpoint, secret key and other constants

class Config(object):
    ENDPOINT = "YOUR ENDPOINT"
    APIM_KEY = "YOUR KEY"
    MODEL_ID = "YOUR MODEL_ID"
    POST_URL = ENDPOINT + "/formrecognizer/v2.0/custom/models/%s/analyze" % MODEL_ID
    UPLOAD_FOLDER = 'app/tempfiles'
    SECRET_KEY = '\xf0?a\x9a\\\xff\xd4;\x0c\xcbHi'
    
    # d11e21fd-66d9-4f3f-b08b-948c5b3a45a4

    # dae412ae-386c-453c-8816-947347bbebe4