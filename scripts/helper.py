import os
import sys
import io
from google.cloud import translate
from google.cloud import vision
import cv2

api_key = os.environ['GT_API_KEY']


#ocr for japanese
def ocr(pic):
	cv2.imshow("Hi", pic)
	cv2.waitKey(0)
	cv2.destroyAllWindows() 
	cv2.imwrite('temp.jpg', pic)
	vision_client = vision.Client(api_key)
	with io.open('temp.jpg', 'rb') as image_file:
		content = image_file.read()
	image = vision_client.image(content=content)
	texts = image.detect_text()
	translations = translate_text(texts)
	return translations
#Target: target language
def translate_text(text):
	trans_client = translate.Client(api_key)
	translation = trans_client.translate(text)
	return translation['translatedText']