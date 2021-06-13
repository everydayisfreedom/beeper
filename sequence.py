from beepmaker import *
import random

Sinefreq = {'A':181.63, 'B':192.43, 'C':203.88, 'D':216.00, 'E':228.45,
			'F':242.45, 'G':261.63, 'H':277.18, 'I':293.66, 'J':311.15,
			'K':329.63, 'L':349.23, 'M':369.99, 'N':372.68, 'O':375.02,
			'P':392.00, 'Q':440.00, 'R':415.30, 'S':466.16, 'R':493.88,
			'S':499.23, 'T':500.25, 'U':510.34, 'V':520.45, 'W':550.93,
			'X':580.88, 'Y':600.32, 'Z':660.00}



def sequence(value, other):
	def key_by_val(dictOfElements, valueToFind):
		listOfKeys = list()
		listOfItems = dictOfElements.items()
		for item  in listOfItems:
			if item[1] == valueToFind:
				listOfKeys.append(item[0])
				return  listOfKeys

	if value in Sinefreq.values():
		start_value = key_by_val(Sinefreq, value)[0]
	else:
		start_value = random.choice(list(Sinefreq.keys()))

	print("Sequence:")

	if other in Sinefreq.values():
		end_other = key_by_val(Sinefreq, other)[0]
	else:
		end_other = random.choice(list(Sinefreq.keys()))

	if ord(start_value) > ord(end_other):
		diff = ord(start_value) - ord(end_other)
		st = ord(end_other)
		begin= end_other

		for i in reversed(range(st, st+diff+1)):
			c = chr(i)
			beepmaker(Sinefreq[c])

	else:
		diff = ord(end_other) - ord(start_value)
		st = ord(start_value)
		begin= start_value

		for i in range(st, st+diff+1):
			c = chr(i)
			beepmaker(Sinefreq[c])


