import Beep

while True:
	text = input('bip ♫ >> ')
	result, error = Beep.play('<stdin>', text)
	
	if error: print(error.as_string())
	else: print(result)
