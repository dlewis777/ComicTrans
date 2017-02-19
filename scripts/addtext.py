import cv2
import sys
sys.path.append('../../MangaTextDetection')
import connected_components as cc
import run_length_smoothing as rls
import clean_page as clean
import ocr
import segmentation as seg
import furigana
import arg
import defaults
from scipy.misc import imsave
import argparse
import os
import scipy.ndimage
import numpy as np
from UnionFind import UnionFind # Taken from https://www.ics.uci.edu/~eppstein/PADS/UnionFind.py
import helper

TEXT_BORDER=7


def white_out_text(img,component,max_size=0,min_size=0,color=(255,255,255)):
	if min_size > 0 and area_bb(component)**0.5<min_size: return
	if max_size > 0 and area_bb(component)**0.5>max_size: return
	#a = area_nz(component,img)
	#if a<min_size: continue
	#if a>max_size: continue
	(ys,xs)=component[:2]
	cv2.rectangle(img,(xs.start,ys.start),(xs.stop,ys.stop),color,-1)

def scale_components(connected_components, factor=TEXT_BORDER):
	new_comps = []
	for component in connected_components:
		new_comps.append((
			slice(component[0].start-factor, component[0].stop+factor),
			slice(component[1].start-factor, component[1].stop+factor),
			))
	return new_comps


def text_within(component, text, x=True):
	shape = cv2.getTextSize(text, cv2.FONT_HERSHEY_PLAIN, 1, 2)[0]
	
	if x:
		return shape[0] <= component[1].stop-component[1].start
	else:
		print component[0].stop - component[0].start
		print shape[1]
		print shape[1]<=component[0].stop - component[0].start
		return shape[1] <= component[0].stop - component[0].start

def add_text(img, component, text=None):
	height = cv2.getTextSize("a", cv2.FONT_HERSHEY_PLAIN, 1, 2)[0][1]
	if text == None:
		line = "a"
		text = ""
		while text_within(component, line, x=True):
			line += "a"
		for i in range(component[0].start + height, component[0].stop+height, height):
			cv2.putText(img, line, (component[1].start, i), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0))

	else:
		index = 0
		line = text[index]
		while text_within(component, line, x=True):
			index += 1
			line += text[index]
		lines = [line]
		for i in range(index, len(text), index):
			lines.append(text[i:i+index])
		lines.append(text[i:])
		for line, i in enumerate(range(component[0].start + height, component[0].stop+height, height)):
			cv2.putText(img, lines[line], (component[1].start, component[0].stop), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0))


def overlaps(comp1, comp2):
	overlaps_y = False
	overlaps_x = False
	#overlaps y
	if comp1[0].start >= comp2[0].start and comp1[0].start <= comp2[0].stop:
		overlaps_y = True
	elif comp2[0].start >= comp1[0].start and comp2[0].start <= comp1[0].stop:
		overlaps_y = True
	#overlaps x
	if comp1[1].start >= comp2[1].start and comp1[1].start <= comp2[1].stop:
		overlaps_x = True
	elif comp2[1].start >= comp1[1].start and comp2[1].start <= comp1[1].stop:
		overlaps_x = True
	return overlaps_y and overlaps_x


def get_connected_components(img):
	components = cc.get_connected_components(segmented_image)
	components = scale_components(components)
	comp_img = np.zeros((img.shape[0], img.shape[1], 1))
	white_out_text(comp_img, components, color=1)
	connected = UnionFind()
	for comp1 in components:
		for comp2 in components:
			if overlaps(comp1,comp2):
				connected.union((comp1[0].start, comp1[0].stop, comp1[1].start, comp1[1].stop),
								 (comp2[0].start, comp2[0].stop, comp2[1].start, comp2[1].stop))
	
	connected_sets = {}
	for child, parent in connected.parents.iteritems():
		if parent not in connected_sets:
			connected_sets[parent] = []
		connected_sets[parent].append(child)

	connected_comps = []

	for a, comps in connected_sets.iteritems():
		min_y = min(comps, key=lambda item: item[0])[0]
		max_y = max(comps, key=lambda item: item[1])[1]
		min_x = min(comps, key=lambda item: item[2])[2]
		max_x = max(comps, key=lambda item: item[3])[3]
		connected_comps.append((slice(min_y, max_y), slice(min_x, max_x)))
	return connected_comps


def translate_page(img, binary_threshold=defaults.BINARY_THRESHOLD):
  gray = clean.grayscale(img)

  inv_binary = cv2.bitwise_not(clean.binarize(gray, threshold=binary_threshold))
  binary = clean.binarize(gray, threshold=binary_threshold)

  segmented_image = seg.segment_image(gray)
  segmented_image = segmented_image[:,:,2]

  components = get_connected_components(segmented_image)

  for component in components:
  	speech = img[component]
  	translation = helper.ocr(speech)
	white_out_text(img, component)
  	add_text(img, component, translation)
  #cc.draw_bounding_boxes(img,components,color=(255,0,0),line_size=2)
  return img
	

if __name__ == '__main__':


  parser = arg.parser
  parser = argparse.ArgumentParser(description='Generate HTML annotation for raw manga scan with detected OCR\'d text.')
  parser.add_argument('infile', help='Input (color) raw Manga scan image to annoate.')
  parser.add_argument('-o','--output', dest='outfile', help='Output html file.')
  parser.add_argument('-v','--verbose', help='Verbose operation. Print status messages during processing', action="store_true")
  parser.add_argument('--display', help='Display output using OPENCV api and block program exit.', action="store_true")
  parser.add_argument('--furigana', help='Attempt to suppress furigana characters which interfere with OCR.', action="store_true")
  #parser.add_argument('-d','--debug', help='Overlay input image into output.', action="store_true")
  parser.add_argument('--sigma', help='Std Dev of gaussian preprocesing filter.',type=float,default=None)
  parser.add_argument('--binary_threshold', help='Binarization threshold value from 0 to 255.',type=int,default=defaults.BINARY_THRESHOLD)
  #parser.add_argument('--segment_threshold', help='Threshold for nonzero pixels to separete vert/horiz text lines.',type=int,default=1)
  parser.add_argument('--additional_filtering', help='Attempt to filter false text positives by histogram processing.', action="store_true")
  arg.value = parser.parse_args()

  infile = arg.string_value('infile')
  outfile = arg.string_value('outfile',default_value=infile + '.text_areas.png')

  if not os.path.isfile(infile):
    print 'Please provide a regular existing input file. Use -h option for help.'
    sys.exit(-1)
  img = cv2.imread(infile)
  translate_page(img)
  cv2.imshow("Hi", img)
  cv2.waitKey(0)
  cv2.destroyAllWindows()  