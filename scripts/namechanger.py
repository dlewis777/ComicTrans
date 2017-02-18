import sys
import subprocess
import os

numb = sys.argv[1]
for filename in os.listdir("/mnt/d/Developement/Hophacks/ComicTrans/enraws/Naruto-" + numb + "-EN/"):
	if filename.endswith(".pdf"):
		parts = filename.split('-')
		print filename

		newname = parts[0].split('_')[1].strip(',') + '_' + parts[2].split('.')[0] + '_' + parts[0].split('_')[0] + '_EN.pdf'
		bashcmd = "mv /mnt/d/Developement/Hophacks/ComicTrans/enraws/Naruto-" + numb + "-EN/" + filename + " /mnt/d/Developement/Hophacks/ComicTrans/enraws/Naruto-" + numb + "-EN/" + newname
		print newname
		process = subprocess.Popen(bashcmd.split(), stdout=subprocess.PIPE)
		output, error = process.communicate()