#First properly working algorithm

import png, random, time, sys, getopt
# Global Definitions
cubeedgewidth = 19
# version = '5.2 len ' + str(cubeedgewidth)
# inimage = 'duck1.png'
# outimage = inimage + 'out' + str(version) + '.png'

# Functions
def maketime(secondsin):
	(min, sec) = divmod(secondsin, 60)
	(hr, min) = divmod(min, 60)
	(day, hr) = divmod(hr, 24)
	
	return '%d day, %d hour, %d min, %d sec' % (day, hr, min, sec)
	
def convertDecToHex(decin):
	hexout = hex(decin).lstrip('0x')
	while len(hexout) < 6:
		hexout = '0' + hexout
	return hexout
		
def processFlatPixels(flatpixels, pixelqty):
	#take in flat list of pixels and convert to a list of r,g,b lists
	groupedpixels = []
	pixelsprocessed = 0
	subpixelsprocessed = 0
	while pixelsprocessed < pixelqty:
		r = flatpixels[subpixelsprocessed]
		subpixelsprocessed += 1
		g = flatpixels[subpixelsprocessed]
		subpixelsprocessed += 1
		b = flatpixels[subpixelsprocessed]
		subpixelsprocessed += 1
		groupedpixels.append([r, g, b])
		pixelsprocessed += 1

	return groupedpixels

def flattenPixelRows(pixelsgrouped):
	flatoutpixels = []
	r = -1
	for row in pixelsgrouped:
		r += 1
		flatoutpixels.append([])
		for pixel in row:
			for i in range(0,3):
				flatoutpixels[r].append(pixel[i])
	return flatoutpixels

def findPixelInRows(pixel):
	for ro in outpixelsgrouped:
		if pixel in ro:
			return True
	return False
	
def genUsableColorCubes(cubeedgewidth):
	#spits out the center coordinates of all color cubes in the color space
	global unusedcolorcubes 
	r = firstmidpoint
	g = firstmidpoint
	b = firstmidpoint
	rmax = 0
	gmax = 0
	bmax = 0

	while r < numberofcolorsperchannel + cubeedgewidth:
		while g < numberofcolorsperchannel + cubeedgewidth:
			while b < numberofcolorsperchannel + cubeedgewidth:
				current = [r,g,b]
				for num in range(0,3):
					if current[num] > numberofcolorsperchannel - 1:
						current[num] -= cubeedgewidth - 1
						if current[num] < numberofcolorsperchannel - 1:
							current[num] = (current[num] + numberofcolorsperchannel - 1) / 2
				unusedcolorcubes.append(current)
				b += cubeedgewidth
			b = firstmidpoint
			g += cubeedgewidth
		g = firstmidpoint
		r += cubeedgewidth
		
	# for color in range(16777216):
		# unusedcolorcubes.append(convertHexToRGB(convertDecToHex(color)))

def findColorDistance(r1, g1, b1, r2, g2, b2):
	#calculate the euclidian distance of 2 colors in 3 dimensions
	return ((r1-r2) ** 2 + (g1 -g2) ** 2 + (b1 -  b2) ** 2) ** .5
	



#File names from command arguments
try:
	opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["inputfile=","outputfile="])
except getopt.GetoptError:
	print 'pix<version>.py -i <inputfile> -o <outputfile>'
	sys.exit(2)

for opt, arg in opts:
	if opt == '-h':
		print 'pix<version>.py -i <inputfile> -o <outputfile>'
		sys.exit()
	elif opt in ("-i", "--inputfile"):
		inimage = arg
	elif opt in ("-o", "--outputfile"):
		outimage = arg

###################################

inprocesscubes = {}
unusedcolorcubes = []

firstmidpoint = float((cubeedgewidth - 1) / float(2))
numberofcolorsinacube = cubeedgewidth ** 3
numberofcolors = 16777216
infile = png.Reader(inimage)
(inx, iny, inpixels) = infile.read_flat()[0:3]
inpixelcount = inx * iny
outrows = [[]]
outpixelsgrouped = [[]]
rowpixel = 0
row = 0
pixelscompleted = 0
starttime = time.time()
exhaustedchunks = []
numberofcolorsperchannel = int(round(numberofcolors ** (1/float(3))))

genUsableColorCubes(cubeedgewidth)
#go through every pixel in the image one by one and find the closest matching color that hasn't been used yet.

inpixelsgrouped = processFlatPixels(inpixels, inpixelcount)

for pixel in inpixelsgrouped:
	# if not findPixelInRows(pixel):
		# outpixelsgrouped[row].append(pixel)
		# pixelscompleted += 1
	# else:
	#check for closest available color cube 

	closestcubecolor = []
	closestcubedistance = 1000000000
	for cubecenter in unusedcolorcubes:
		cubedistance = findColorDistance(pixel[0], pixel[1], pixel[2], cubecenter[0], cubecenter[1], cubecenter[2])
		if cubedistance < closestcubedistance:
			closestcubedistance = cubedistance
			closestcube = cubecenter
			cubecoordstring = '%s%s%s' %(closestcube[0], closestcube[1], closestcube[2])

	#once the closest available cube is found, check to see if it's an in-process cube that has some colors used already
	if inprocesscubes.has_key(cubecoordstring):

		cubecolordistance = 1000000000
		
		for cubepixel in inprocesscubes[cubecoordstring]:
			calculatedcolordistance = findColorDistance(pixel[0], pixel[1], pixel[2], cubepixel[0], cubepixel[1], cubepixel[2])
			if calculatedcolordistance < cubecolordistance:
				closestcubecolor = cubepixel
				cubecolordistance = calculatedcolordistance
		try:
			inprocesscubes[cubecoordstring].remove(closestcubecolor)
		except:
			print 'hmm1'
		if len(inprocesscubes[cubecoordstring]) == 0:
			unusedcolorcubes.remove(cubecenter)

			inprocesscubes.pop(cubecoordstring)


	#if there isn't an in-process cube, create a new one and and remove the current color from it
	else:

		#inprocesscubes is a dictionary with the cube coordinates as the keys. Available colors from a given cube will be listed under that key

		inprocesscubes[cubecoordstring] = []
		for r in range(int(closestcube[0] - firstmidpoint), int(closestcube[0] + firstmidpoint + 1)):
			for g in range(int(closestcube[1] - firstmidpoint), int(closestcube[1] + firstmidpoint + 1)):
				for b in range(int(closestcube[2] - firstmidpoint), int(closestcube[2] + firstmidpoint + 1)):
					
					inprocesscubes[cubecoordstring].append([r, g, b])
					
		#clean up edge pixels that go beyond the 0-255 color boundries
		if closestcube[0] - firstmidpoint < 0 or closestcube[1] - firstmidpoint < 0 or closestcube[2] - firstmidpoint < 0 or closestcube[0] + firstmidpoint > 255 or closestcube[1] + firstmidpoint > 255 or closestcube[2] + firstmidpoint > 255:
			#duplicate the current dictionary entry so we can edit it when we find bad entries (if we don't do this it messes up the indexing so the loop doesn't work)
			diccopy = list(inprocesscubes[cubecoordstring])
			for p in diccopy:
				if p[0] < 0 or p[1] < 0 or p[2] < 0 or p[0] > 255 or p[1] > 255 or p[2] > 255:
					
					inprocesscubes[cubecoordstring].remove(p)

		#for edge cubes we need to remove their extra colors that would overlap the normal cubes. I do this by only allowing the inside edge to extend the distance the center is from the outside edge
		#check if the current cube is an edge cube
		for c in closestcube:
			#if it is an edge cube, go through every pixel and make sure it doesn't overlap. If it does, remove that pixel from the edge cube. 
			if c + firstmidpoint > numberofcolorsperchannel:
				for rgb in inprocesscubes[cubecoordstring]:
					if rgb[0] < closestcube[0] - firstmidpoint or rgb[1] < closestcube[1] - firstmidpoint or rgb[2] < closestcube[2] - firstmidpoint:
						inprocesscubes[cubecoordstring].remove(rgb)
						
						
		#direct availble pixel match found
		if pixel in inprocesscubes[cubecoordstring]:
			inprocesscubes[cubecoordstring].remove(pixel)
			closestcubecolor = pixel
		#direct match not found. Find the closest in the cube
		else:

			# if cubecoordstring == '244.5244.5244.5':
				# print str(inprocesscubes[cubecoordstring])
			cubecolordistance = 1000000000
			for cubepixel in inprocesscubes[cubecoordstring]:
				d = findColorDistance(pixel[0], pixel[1], pixel[2], cubepixel[0], cubepixel[1], cubepixel[2])
				if  d < cubecolordistance:
					closestcubecolor = cubepixel
					cubecolordistance = d
			inprocesscubes[cubecoordstring].remove(closestcubecolor)
		if len(inprocesscubes[cubecoordstring]) == 0:
			try:
				unusedcolorcubes.remove(cubecoordstring)
			except:
				print 'hmm'
	outpixelsgrouped[row].append(closestcubecolor)
	pixelscompleted += 1

	rowpixel += 1
	#if we've reached the end of the row for the outrows list, start saving to the next row
	if rowpixel == inx and row < iny - 1:
		row += 1
		
		print inimage
		print 'row ' + str(row)
		print str(float(row/float(iny)*100)) + "% complete "
		print 'time elapsed = ' + maketime(time.time() - starttime) + '\n'
		outpixelsgrouped.append([])
		rowpixel = 0

#count the number of duplicate pixels in the image


			
	
outfile = file(outimage, 'wb')
outpng = png.Writer(width = inx, height = iny)
outpng.write(outfile, flattenPixelRows(outpixelsgrouped))
outfile.close()
print 'Total time elapsed = ' + maketime(time.time() - starttime)
print time.time() - starttime