from helpers.response import make_response
import logging
import traceback


def handle_exception(ex: Exception, payload: dict):
    logging.error(
        f"Showing error traceback from {handle_exception.__name__}: {traceback.format_exc()}"
    )
    if "permission denied" in str(ex):
        return make_response(
            status=401,
            data=f"User: {payload.get('database_info', {}).get('username')}  dose not have permission on the table: {payload.get('database_info', {}).get('table_name')}",
        )
    elif "Database not found for the provided database name" in str(ex):
        return make_response(
            status=403,
            data=f"Database not found for the provided database name: {payload.get('database_info', {}).get('database_name')}",
        )
    elif "failed: FATAL:  database" in str(ex):
        return make_response(
            status=403,
            data=f"Database not found for the provided database name: {payload.get('database_info', {}).get('database_name')}",
        )
    elif "password authentication failed for user" in str(ex):
        return make_response(
            status=403,
            data=f"Password authentication failed for user: {payload.get('database_info', {}).get('username')} for the database name: {payload.get('database_info', {}).get('database_name')}",
        )
    else:
        return make_response(status=400, data=str(ex))
