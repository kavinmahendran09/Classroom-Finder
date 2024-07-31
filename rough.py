import pandas as pd
from datetime import datetime, timedelta

# Define a global variable for the current day order
global_current_day_order = None

# Function to round time to the next nearest 5 minutes
def round_time_to_nearest_five(current_time):
    time_obj = datetime.strptime(current_time, "%H:%M")
    minute = time_obj.minute
    remainder = minute % 5
    if remainder != 0:
        new_minute = minute + (5 - remainder)
        if new_minute == 60:
            time_obj += timedelta(hours=1)
            new_minute = 0
    else:
        new_minute = minute
    
    rounded_time = time_obj.replace(minute=new_minute, second=0).strftime("%H:%M")
    return rounded_time

# Function to find free rooms
def find_free_rooms(custom_time=None, custom_day_order=None, custom_day=None):
    global global_current_day_order  # Declare the global variable inside the function

    # Load CSV files
    unified_timetable = pd.read_csv("UNIFIED_TIME_TABLE.csv")
    detailed_timetable = pd.read_csv("detailed_timetable.csv")
    day_order_df = pd.read_csv("2024_Day_order.csv")

    # Define time slots
    time_slots = [
        ("08:00", "08:50"), ("08:50", "09:40"), ("09:45", "10:35"), ("10:40", "11:30"),
        ("11:35", "12:25"), ("12:30", "13:20"), ("13:25", "14:15"), ("14:20", "15:10"),
        ("15:10", "16:00"), ("16:00", "16:50"), ("16:50", "17:30"), ("17:30", "18:10")
    ]

    # Get current time
    if custom_time:
        current_time = custom_time
    else:
        current_time = datetime.now().strftime("%H:%M")

    # Check if the current time is before 8:00 AM or after 4:50 PM
    if current_time < "08:00":
        return "College not yet started."
    elif current_time > "16:50":
        return "College over."

    # Get current date and corresponding day order
    if custom_day_order:
        current_day_order = custom_day_order
    else:
        if custom_day:
            current_date = datetime.strptime(custom_day, "%d %B %Y")
        else:
            current_date = datetime.now()

        # Adjust the date format to match the CSV file
        current_day = current_date.strftime("%d").lstrip("0")  # Remove leading zeros from the day
        current_month = current_date.strftime("%B")
        day_order_row = day_order_df[(day_order_df['Date'].astype(str) == current_day) &
                                     (day_order_df['Month'] == current_month)]

        # Check if the day order is NULL or day_order_row is empty
        if day_order_row.empty or pd.isnull(day_order_row['Day_order'].values[0]):
            return "College doesn't run today."

        current_day_order = int(day_order_row['Day_order'].values[0])

    # Update the global variable
    global_current_day_order = current_day_order

    # Find the current time slot
    current_time_slot = None
    for start, end in time_slots:
        if start <= current_time <= end:
            current_time_slot = f"{start} - {end}"
            break

    # Initialize free_rooms as an empty list
    free_rooms = []
    if current_time_slot is None:
        next_update_time = round_time_to_nearest_five(current_time)
        return f"Free rooms get updated at: {next_update_time}"
    else:
        # Find occupied rooms from the unified timetable
        occupied_rooms = set()

        occupied_rooms.update(
            unified_timetable.loc[(unified_timetable['Day'] == f"Day {current_day_order}") &
                                  (unified_timetable['Time Slot'] == current_time_slot),
                                  'Room Number'].tolist()
        )

        # Map slot to room number from the detailed timetable
        detailed_slots = detailed_timetable['Slot'].tolist()
        detailed_rooms = detailed_timetable['RoomNo.'].tolist()
        detailed_room_map = dict(zip(detailed_slots, detailed_rooms))

        # Identify occupied rooms in the detailed timetable based on the current time slot
        for course_code in unified_timetable.loc[
            (unified_timetable['Day'] == f"Day {current_day_order}") & 
            (unified_timetable['Time Slot'] == current_time_slot),
            'Course Code'
        ]:
            slot = course_code.split('/')[0]
            room_number = detailed_room_map.get(slot, "Unknown")
            occupied_rooms.add(room_number)

        # List all possible rooms
        all_rooms = set(unified_timetable['Room Number'].unique()).union(set(detailed_timetable['RoomNo.'].unique()))

        # Find free rooms and remove 'Unknown'
        free_rooms = [room for room in list(all_rooms - occupied_rooms) if room != "Unknown"]

    return free_rooms

# Get the free rooms and print the current day order
free_rooms = find_free_rooms()
print("Free classrooms right now are:", free_rooms)
print("Global current day order:", global_current_day_order)
