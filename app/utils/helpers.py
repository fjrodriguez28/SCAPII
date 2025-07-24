def standard_response(data=None, message="OK", success=True):
    return {
        "success": success,
        "message": message,
        "data": data
    }
