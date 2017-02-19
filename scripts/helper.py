#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import io
from google.cloud import translate
from google.cloud import vision
from yandex_translate import YandexTranslate
import cv2
import time
api_key = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
 #ocr for japanese
def ocr(pic, target_lang="en"):
	#print api_key
	#print pic
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
		# print("translate:")
		#print(text.description)
		# print("to")
		# print(google_translate(text.description.strip()))
		# print("end translate\n")
		translations.append(google_translate(text.description.strip(), target_lang))
		#time.sleep(.1)
	# 	print text.description
	# 	print google_
	# print " ".join(translations)

	return " ".join(translations)
#Target: target language

def google_translate(text, target_lang):
	# print("translating text")
	# print(text)
	# print("under text")
	trans_client = translate.Client()
	translation = trans_client.translate(text, target_language=target_lang)

	# print("finished translation")
	return translation['translatedText']