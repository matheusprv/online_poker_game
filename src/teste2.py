import threading

# Global variables
v1 = None
v2 = None
v3 = None

# Event objects to signal when variables are updated
v1_event = threading.Event()
v2_event = threading.Event()
v3_event = threading.Event()

# Lock for accessing variables safely
lock = threading.Lock()

# Function for thread 1
def thread1_func():
    global v1, v1_event
    while True:
        v1_event.wait()  # Wait until v1 is set
        with lock:
            print("Thread 1: v1 =", v1)
        v1_event.clear()  # Reset event for next iteration

# Function for thread 2
def thread2_func():
    global v2, v2_event
    while True:
        v2_event.wait()  # Wait until v2 is set
        with lock:
            print("Thread 2: v2 =", v2)
        v2_event.clear()  # Reset event for next iteration

# Function for thread 3
def thread3_func():
    global v3, v3_event
    while True:
        v3_event.wait()  # Wait until v3 is set
        with lock:
            print("Thread 3: v3 =", v3)
        v3_event.clear()  # Reset event for next iteration

# Main function to interact with the user
def main():
    global v1, v2, v3, v1_event, v2_event, v3_event

    while True:
        user_input = input("Enter a value for v1, v2, or v3 (e.g., v1=10): ")
        try:
            var, value = user_input.split('=')
            value = int(value)
            with lock:
                if var == "v1":
                    v1 = value
                    v1_event.set()  # Signal thread 1
                elif var == "v2":
                    v2 = value
                    v2_event.set()  # Signal thread 2
                elif var == "v3":
                    v3 = value
                    v3_event.set()  # Signal thread 3
        except ValueError:
            print("Invalid input. Please enter in the format 'v1=10', 'v2=20', or 'v3=30'.")

# Create and start threads
thread1 = threading.Thread(target=thread1_func)
thread2 = threading.Thread(target=thread2_func)
thread3 = threading.Thread(target=thread3_func)

thread1.start()
thread2.start()
thread3.start()

# Start main
main()
