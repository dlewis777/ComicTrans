import os
import sys
import io
from google.cloud import translate
from google.cloud import vision
import cv2
import time
api_key = os.environ['GT_API_KEY']


#ocr for japanese
def ocr(pic):
	# cv2.imshow("Hi", pic)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows() 
	cv2.imwrite('temp.jpg', pic)
	vision_client = vision.Client(api_key)
	with io.open('temp.jpg', 'rb') as image_file:
		content = image_file.read()
	image = vision_client.image(content=content)
	texts = image.detect_text()
	translations = []
	for text in texts:
		print "translate:"
		print text.description
		print "to"
		print translate_text(text.description)
		print "end translate\n"
		translations.append(translate_text(text.description))
		time.sleep(.1)
		#print translations
	return "".join(translations)
#Target: target language
def translate_text(text):
	print "translating text"
	print text
	trans_client = translate.Client(api_key)
	translation = trans_client.translate(text)
	print "finished translation"
	return translation['translatedText']