# Open a file
path=r'C:\Users\Dan\Documents\Python\test.txt'
fo = open(path, "r+")
print ("Name of the file: " +  fo.name)

# Assuming file has following 5 lines
# This is 1st line
# This is 2nd line
# This is 3rd line
# This is 4th line
# This is 5th line

line = fo.readline()
print ("Read Line: " + line)

# Now truncate remaining file.
#fo.truncate()

# Try to read file now
line = fo.readline()
print ("Read Line: " + line)

# Close opend file
fo.close()
