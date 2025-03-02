import time
from datetime import datetime

def show_time_and_date():
    # Use time module to show current time
    current_time = time.strftime("%H:%M:%S")
    # Use datetime module to show the current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    # print(f"Current Time: {current_time}")
    # print(f"Current Date: {current_date}")
    z=str(current_date)+','+str(current_time)

    return z
