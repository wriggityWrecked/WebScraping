
def check_response_status(status_code):
    if status_code == 204 or status_code >= 400 or status_code >= 500:
        return False
    return True
