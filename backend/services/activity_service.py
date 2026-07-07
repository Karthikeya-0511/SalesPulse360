activity_log = []

def add_activity(message):
    from datetime import datetime

    activity_log.insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": message
    })

    if len(activity_log) > 20:
        activity_log.pop()


def get_activity():
    return activity_log