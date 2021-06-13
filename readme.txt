+++++
Requirements:

PyAudio

+++++
How to Beep:

Beep introduces four new operators (Beepers), and one known. Familiar, yet, not so familiar:

•	+ >> The Next Beeper is used to signify a sequence of sounds that will be played one after the other. A + B, will play out the sound retaining to A, and then B will be played afterwards.

•	- >> The Pause Beeper produces a slight pause before playing a sound that is in succession of another sound. A – B, will play A, pause, then play B.

•	* >> The Simultaneous Beeper will play two or more sounds at the same time. A * B, will superpose the two sounds then play it out.

•	/ >> The Sequence Beeper will play a number of sounds ranging from one letter frequency to another. A/E, will play sounds ranging from A to E in that order, and vice versa. 

•	( ) >>  Parenthesis used for precedence. It is also possible to use Keynotes with a number of different operators: (A + B) – C *D


Beepers have an order of precedence associated with them. The Sequence and Simultaneous Beepers have a higher precedence than the Next and Pause Beepers. Precedence was thought of by a member not to be of importance, but to avoid any ambiguity in our language, we decided to add it to the implementation of the language. An upper bound and lower bound of frequencies have also been set, and so if  there is a chosen frequency that crosses these bounds, a random frequency value will be given. 

Our sound was unable to be generated using PyCharm and the Python Shell, but we were able to produce sound using Sublime Text. But given that Sublime Text cannot take inputs we had to add the input as part of the code within a variable. We will send the Shell to test the code, but also a separate file with the variable containing the code, in case you run into the same problem. A demo will also be sent. 

+++++
Beep’s BNF Grammar:

<Start symbol> ==> <SOUND>

<SOUND> ==> <SOUND> '+' <KEYNOTES> | <SOUND> '+' <KEYNOTES> | <KEYNOTES>

<KEYNOTES> ==> <KEYNOTES> '*' <KEY> | <KEYNOTES> '/' <KEY> | <KEY>

<KEY> ==> A | B | C | ... | Y | Z


+++++
Beep’s Regular Expression:

L(M) = {(KEY ( + | - | * | / ) )+ KEY }


