import pandas as pd

# Detailed timetable data
detailed_timetable_data = {
    'Slot': ['A', 'B', 'C', 'D', 'F', 'G', 'P13-P14', 'L11-L12', 'L21-L22', 'P49-P50'],
    'RoomNo.': ['UB 1206', 'UB 1206', 'UB 1206', 'UB 1206', 'UB 1206', 'TP 906', 'UB 714A', 'UB 713B', 'UB 1206', 'TP 1317-WIN Lab']
}

# Provided timetable data
timetable_data = {
    'Hour/Day Order': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
    'Day 1': ['A', 'A / X', 'F / X', 'F', 'G', 'P6', 'P7', 'P8', 'P9', 'P10', 'L11', 'L12'],
    'Day 2': ['P11', 'P12/X', 'P13/X', 'P14', 'P15', 'B', 'B', 'G', 'G', 'A', 'L21', 'L22'],
    'Day 3': ['C', 'C / X', 'A / X', 'D', 'B', 'P26', 'P27', 'P28', 'P29', 'P30', 'L31', 'L32'],
    'Day 4': ['P31', 'P32/X', 'P33/X', 'P34', 'P35', 'D', 'D', 'B', 'E', 'C', 'L41', 'L42'],
    'Day 5': ['E', 'E / X', 'C / X', 'F', 'D', 'P46', 'P47', 'P48', 'P49', 'P50', 'L51', 'L52']
}

# Convert the timetable data into a DataFrame
timetable_df = pd.DataFrame(timetable_data)

# Define the 24-hour time slots
time_slots_24hr = [
    "08:00 - 08:50", "08:50 - 09:40", "09:45 - 10:35", "10:40 - 11:30", 
    "11:35 - 12:25", "12:30 - 13:20", "13:25 - 14:15", "14:20 - 15:10", 
    "15:10 - 16:00", "16:00 - 16:50", "16:50 - 17:30", "17:30 - 18:10"
]

# Reshape the timetable_df to long format for merging with time_slots and room numbers
timetable_long_df = timetable_df.melt(id_vars='Hour/Day Order', var_name='Day', value_name='Course Code')
timetable_long_df['Time Slot'] = timetable_long_df['Hour/Day Order'].map(lambda x: time_slots_24hr[int(x)-1])
timetable_long_df.drop(columns=['Hour/Day Order'], inplace=True)

# Create a DataFrame for the detailed timetable
detailed_timetable_df = pd.DataFrame(detailed_timetable_data)
detailed_timetable_df.columns = ['Course Code', 'Room Number']

# Handle "A / X" format in Course Code
def get_room_number(course_code, detailed_df):
    codes = course_code.split('/')
    codes = [code.strip() for code in codes]
    for code in codes:
        room_number = detailed_df[detailed_df['Course Code'] == code]['Room Number']
        if not room_number.empty:
            return room_number.values[0]
    return 'Unknown'

# Apply the function to get the correct room number
merged_timetable_df = timetable_long_df.copy()
merged_timetable_df['Room Number'] = merged_timetable_df['Course Code'].apply(lambda x: get_room_number(x, detailed_timetable_df))

# Rearrange columns to match the format of UNIFIED_TIME_TABLE.csv
merged_timetable_df = merged_timetable_df[['Day', 'Time Slot', 'Course Code', 'Room Number']]

# Save the resulting DataFrame as a new CSV file
output_path_24hr = 'NEW_UNIFIED_TIME_TABLE_24HR.csv'
merged_timetable_df.to_csv(output_path_24hr, index=False)

# Display the resulting DataFrame
merged_timetable_df.head()
