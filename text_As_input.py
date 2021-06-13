import Beep

while True:
    text = "A/B + Z "
    result, error = Beep.run('<stdin>', text)

    if error: print(error.as_string())
    else: print("end")
    break


