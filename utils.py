def levenshtein(a, b):
	lena = len(a)
	lenb = len(b)

	# if one of the two strings are empty return 1
	if 0 in [lena, lenb]: return 1

	# matrix initialization
	# the first row is initialized with 0..lenb
	matrix = [[i for i in range(lenb+1)]]+[[0]*(lenb+1) for i in range(lena)]

	# the first column is initialized with 0..lena
	for i in range(1, lena+1):
		matrix[i][0] = i

	for i in range(1, lena+1):
		c = a[i-1]
		for j in range(1, lenb+1):
			cost = 0 if c==b[j-1] else 1
			matrix[i][j] = dist = min(
				matrix[i - 1][j] + 1, # left
				matrix[i][j - 1] + 1, # up
				matrix[i - 1][j - 1] + cost # corner
			)

	# the distance is matrix[-1][-1]
	# the difference ratio is the distance divided by the greatest length of the two strings
	return dist/max(lena, lenb)

def is_lua(view, position=None):
	if view is None:
		return False

	# get the position of the carret
	if position is None:
		try:
			position = view.sel()[0].begin()
		except:
			return False

	return view.match_selector(position, 'source.lua')