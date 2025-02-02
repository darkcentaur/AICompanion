import time

# Counting time using thread
def print_waiting_time(response_received):
    start_time = time.time()
    while not response_received.is_set():
        elapse_time = time.time() - start_time
        print(f"Waiting time: {elapse_time:.2f} seconds", end="\r")
        time.sleep(1)
    print("\nResponse received.")
