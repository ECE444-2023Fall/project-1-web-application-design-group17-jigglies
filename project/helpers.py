from datetime import datetime

def parseDateTime(date, start_time, end_time):
    ''' Takes the date, start_time, end_time of the Event table as input, and formats into October 31, 2023 @ 9AM-3PM'''
    formatted_date = date.strftime("%B %d, %Y")
    formatted_start_time = start_time.strftime("%I%p").lstrip('0')
    formatted_end_time = end_time.strftime("%I%p").lstrip('0')

    # Create the final formatted string
    formatted_string = f"{formatted_date} @ {formatted_start_time}-{formatted_end_time}"
    return formatted_string