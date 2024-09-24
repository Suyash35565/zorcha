from datetime import datetime

def convert_epoch_to_human_readable(epoch_time):
    # Convert epoch time from milliseconds to seconds
    dt = datetime.fromtimestamp(epoch_time / 1000)
    # Format the datetime object to the desired string format
    human_readable = dt.strftime('%d/%m/%Y, %I:%M:%S %p')
    return human_readable