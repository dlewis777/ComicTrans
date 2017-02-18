import sys
import os
numb = sys.argv[1]

path = "/mnt/d/Developement/Hophacks/ComicTrans/enraws/Naruto-"
for filename in os.listdir(path + numb + "-EN/"):
	if filename.endswith(".pdf"):

		pdf = file(path + numb + "-EN/" + filename, "rb").read()

		startmark = "\xff\xd8"
		startfix = 0
		endmark = "\xff\xd9"
		endfix = 2
		i = 0

		njpg = filename.split('.')[0]
		while True:
		    istream = pdf.find("stream", i)
		    if istream < 0:
		        break
		    istart = pdf.find(startmark, istream, istream+20)
		    if istart < 0:
		        i = istream+20
		        continue
		    iend = pdf.find("endstream", istart)
		    if iend < 0:
		        raise Exception("Didn't find end of stream!")
		    iend = pdf.find(endmark, iend-20)
		    if iend < 0:
		        raise Exception("Didn't find end of JPG!")
		     
		    istart += startfix
		    iend += endfix
		    print "JPG %s from %d to %d" % (njpg, istart, iend)
		    jpg = pdf[istart:iend]
		    jpgfile = file(path + numb + "-EN/%s.jpg" % njpg, "wb")
		    jpgfile.write(jpg)
		    jpgfile.close()
		     
		    #njpg += 1
		    i = iend