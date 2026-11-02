import speech_recognition as sr  # Speech recognition ke liye library import karta hai.


def main():
    r = sr.Recognizer()  # Recognizer object banata hai jo audio ko text mein convert karega.
    with sr.Microphone() as source: # This line is used to ask for the user microphone access
        r.adjust_for_ambient_noise(source) # this will implement the noice cancellation here 
        r.pause_threshold = 2 # Now if user pauses for 2 seconds then we are going to start the process to convert it into text 

        print("Speak something.....")
        audio = r.listen(source) # here we are gonna get the user audio 


        print("Processing Audio .... (STT)")
        stt = r.recognize_google(audio) # and here we are gonna able to process it

        print("You Said:", stt) # and print it on the screen 


if __name__ == "__main__":  # File ko direct run karne par hi main function chalata hai.
    main()  # Microphone se audio lekar speech recognition start karta hai.