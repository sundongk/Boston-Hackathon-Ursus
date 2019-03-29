import RPi.GPIO as GPIO     # importing GPIO library
import time                 # importing time library for delay

from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

import re

app = Flask(__name__)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    """Receive text containing user instructions and sends to the arduino circuit to turn/off switch and replies with a message"""
    time_input = 0 # Indicator to show when exactly user wants to turn on/off light
    on_command = "on"
    off_command = "off"
    time_command = 0 # Indicator to show when exactly user wants to turn on/off light
    time_indicator = 0 # Counter to show if user entered a time
    turn_on_indicator = 0 # Indicator will be 1 if user wants to turn on light
    turn_off_indicator = 0 # Indicator will be 1 if user wants to turn off light
    resp = MessagingResponse()

    p = GPIO.PWM(11, 50)
    p.start(7.5)

    try:
        while True:
            of = open("status.txt", 'r')
            statustxt = of.read()

            current_status = int(statustxt)

            of.close()


            text = body.lower() # Make text all lowercase to consolidate possibilities

            text_list = re.sub("[^\w]", " ", text).split() # Split text into list of words

            if len(text) == 6 and text == 'status':
                if current_status == 0:
                    status_string = "off"
                else:
                    status_string = "on"

                resp.message("Your lights are currently " + status_string)
                return str(resp)

            else:
                for i in text_list:
                    if i == on_command:
                        turn_on_indicator = 1
                    elif i == off_command:
                        turn_off_indicator = 1
                    elif i.isdigit():
                        time_command = int(i)
                        time_indicator = 1


            wf = open("status.txt", 'w')

            if (turn_on_indicator + turn_off_indicator == 1) and (time_indicator == 0):
                if turn_on_indicator == 1:
                    if current_status == 0:
                        wf.write("1")
                        wf.close()
                        resp.message ("Turning on lights!")
                        p.ChangeDutyCycle(2.5)
                        time.sleep(1)
                        return str(resp)
                    else:
                        wf.write("1")
                        wf.close()
                        resp.message("Your lights are already on!")
                        return str(resp)
                if turn_off_indicator == 1:
                    if current_status == 1:
                        wf.write("0")
                        wf.close()
                        resp.message("Turning off lights!")
                        p.ChangeDutyCycle(12.5)
                        time.sleep(1)
                        return str(resp)
                    else:
                        wf.write("0")
                        wf.close()
                        resp.message("Your lights are already off!")
                        return str(resp)

            if (turn_on_indicator + turn_off_indicator != 1) or (time_indicator != 1) :
                wf.write(str(current_status))
                wf.close()
                resp.message ("Error: invalid command")
                return str(resp)

            else:



                if turn_on_indicator == 1:
                    if current_status == 0:
                        wf.write("1")
                        wf.close()
                        resp.message("Turning on light in " + str(time_command) + " minutes")
                        time.sleep(time_command * 60)
                        p.ChangeDutyCycle(2.5)
                        time.sleep(1)
                        return str(resp)
                    else:
                        wf.write("1")
                        wf.close()
                        resp.message("Your lights are already on!")
                        return str(resp)
                if turn_off_indicator == 1:
                    if current_status == 1:
                        wf.write("0")
                        wf.close()
                        resp.message("Turning off light in " + str(time_command) + " minutes")
                        time.sleep(60 * time_command)
                        p.ChangeDutyCycle(12.5)
                        time.sleep(1)
                        return str(resp)
                    else:
                        wf.write("0")
                        wf.close()
                        resp.message("Your lights are already off!")
                        return str(resp)

    except KeyboardInterrupt:
            GPIO.cleanup()

    # Start our TwiML response
    # Determine the right reply for this message

if __name__ == "__main__":
    app.run()
