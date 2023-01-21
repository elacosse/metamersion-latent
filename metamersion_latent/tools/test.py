import signal


def timeout_handler(signum, frame):
    raise TimeoutError("Timeout")


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)
while True:
    try:
        user_input = input("Enter something: ")
        signal.alarm(0)
    except TimeoutError:
        print("Sorry, time is up.")
        user_input = None
