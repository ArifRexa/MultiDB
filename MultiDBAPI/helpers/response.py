from blacksheep.server.responses import status_code
import logging


def make_response(status=200, data=None):
    try:
        if isinstance(data, Exception):
            arguments = data.args
            if len(arguments) >= 2:
                code = data.args[1].get("status_code", None)
                if code:
                    return status_code(code, data.args[0])
                else:
                    return status_code(status, str(data))
    except Exception as ex:
        logging.error(f"Exception happened from make response function : {ex}")

    return status_code(status, message=data)
