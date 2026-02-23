from datetime import datetime
import random
import os
from logger import setup_default_logging, get_logger
from logging import Logger

ENDPOINTS = ["/api/v1/resource", "/api/v1/users", "/api/v1/items"]
METHODS = ["GET", "POST", "PUT", "DELETE"]
STATUS_CODES = [200, 201, 400, 401, 403, 404, 500]

TRACEBACKS = {
    400: [
        "Traceback (most recent call last):\n  File \"app/api/routes.py\", line 87, in create_user\n    validated = UserSchema().load(request.json)\nmarshmallow.exceptions.ValidationError: {'email': ['Not a valid email address.'], 'username': ['Missing data for required field.']}\n",
        "Traceback (most recent call last):\n  File \"app/api/routes.py\", line 134, in update_item\n    item_id = int(request.args.get('id'))\nValueError: invalid literal for int() with base 10: 'abc'\n",
    ],
    401: [
        "Traceback (most recent call last):\n  File \"app/middleware/auth.py\", line 45, in verify_token\n    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\njwt.exceptions.ExpiredSignatureError: Signature has expired\n",
        "Traceback (most recent call last):\n  File \"app/middleware/auth.py\", line 52, in verify_token\n    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\njwt.exceptions.InvalidTokenError: Token is missing required claims\n",
    ],
    403: [
        "Traceback (most recent call last):\n  File \"app/middleware/permissions.py\", line 23, in check_permissions\n    assert user.role in required_roles, f\"User role '{user.role}' not in {required_roles}\"\nAssertionError: User role 'viewer' not in ['admin', 'editor']\n",
    ],
    404: [
        "Traceback (most recent call last):\n  File \"app/api/routes.py\", line 62, in get_user\n    user = db.query(User).filter_by(id=user_id).one()\nsqlalchemy.orm.exc.NoResultFound: No row was found when one was required\n",
        "Traceback (most recent call last):\n  File \"app/api/routes.py\", line 98, in get_item\n    item = db.query(Item).filter_by(id=item_id).one()\nsqlalchemy.orm.exc.NoResultFound: No row was found when one was required\n",
    ],
    500: [
        "Traceback (most recent call last):\n  File \"app/api/routes.py\", line 201, in process_resource\n    result = db.execute(query)\n  File \"app/db/session.py\", line 34, in execute\n    return self.connection.execute(statement)\nsqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server: Connection refused\n",
        "Traceback (most recent call last):\n  File \"app/services/user_service.py\", line 78, in process_batch\n    results = [self._transform(item) for item in data]\n  File \"app/services/user_service.py\", line 91, in _transform\n    return {\"id\": item[\"id\"], \"value\": item[\"value\"] / item[\"count\"]}\nZeroDivisionError: division by zero\n",
        "Traceback (most recent call last):\n  File \"app/workers/background.py\", line 45, in run_task\n    result = task.execute()\n  File \"app/tasks/report.py\", line 67, in fetch_data\n    response = requests.get(EXTERNAL_API_URL, timeout=5)\nrequests.exceptions.Timeout: HTTPConnectionPool(host='analytics.internal', port=8080): Read timed out.\n",
    ],
}


def generate_line():
    """Generate a single mock log line with optional traceback for error status codes."""
    timestamp = datetime.now().isoformat()
    method = random.choice(METHODS)
    endpoint = random.choice(ENDPOINTS)
    status_code = random.choice(STATUS_CODES)
    response_time = random.randint(10, 5000)  # ms
    log_line = f"{timestamp} - {method} - {endpoint} - {status_code} - {response_time}ms\n"
    if status_code not in (200, 201):
        traceback = random.choice(TRACEBACKS[status_code])
        return log_line + traceback
    return log_line


def make_logs(log_file_size=8_000_000, file_path: str = "mock_logs.log", logger_instance: Logger = None):  # approx 500mb
    with open(file_path, "w") as f:
        for _ in range(log_file_size):
            f.write(generate_line())
    file_size = os.path.getsize(file_path)
    if logger_instance:
        logger_instance.info(
            f"Generated log file of size: {file_size / (1024 * 1024):.2f} MB at {file_path}")


if __name__ == "__main__":
    logger = get_logger()
    setup_default_logging()
    make_logs(logger_instance=logger)
