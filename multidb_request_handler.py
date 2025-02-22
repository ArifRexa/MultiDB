import requests
import json
import logging
import os


class DatabaseOperation:
    """
    This class is responsible for communicating with the MultiDBAPI to get data from the different database and different
    table. We have to pass database info when initiate the class. Then we need to send a request to the MultiDBAPI to
    get the data with sending url and endpoints.
    """

    def __init__(
        self,
        database_name: str = None,
        table_name: str = None,
        username: str = None,
        password: str = None,
        host: str = None,
        port: str = None,
    ):
        self._database_name = database_name
        self._table_name = table_name
        self._username = username
        self._password = password
        self.headers = {"Content-Type": "application/json"}
        self._host = host
        self._port = port
        self._url = f"{self._host}:{self._port}/"

    def make_request(
        self,
        method: str,
        endpoint: str = None,
        data: dict = None,
        headers: dict = None,
        url: str = None,
    ):
        if headers is not None:
            self.headers.update(headers)

        if url is None:
            url = self._url

        database_info = self._create_database_info_payload()
        database_info.update({"data": data})
        payload = json.dumps(database_info)
        # logging.info(f"Sending request to {url + endpoint} with the payload: {payload}")

        response = requests.request(
            method, url + endpoint, headers=self.headers, data=payload
        )
        logging.info(f"response code: {response.status_code}")
        response_text = None
        try:
            response_text = response.json()
        except ValueError:
            response_text = response.text

        return response.status_code, response_text

    def get_request(self, endpoint: str, params=None, data: dict = None):
        return self.make_request("GET", endpoint, data=data)

    def post_request(
        self,
        endpoint: str = None,
        data: dict = None,
        headers: dict = None,
        url: str = None,
    ):
        return self.make_request("POST", endpoint, data=data, headers=headers, url=url)

    def patch_request(
        self,
        endpoint: str = None,
        data: dict = None,
        headers: dict = None,
        url: str = None,
    ):
        return self.make_request("PATCH", endpoint, data=data, headers=headers, url=url)

    def delete_request(
        self,
        endpoint: str = None,
        data: dict = None,
        headers: dict = None,
        url: str = None,
    ):
        return self.make_request(
            "DELETE", endpoint, data=data, headers=headers, url=url
        )

    def _create_database_info_payload(self):
        return {
            "database_info": {
                "database_name": self._database_name,
                "table_name": self._table_name,
                "username": self._username,
                "password": self._password,
            }
        }


if __name__ == "__main__":
    obj = DatabaseOperation(host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
                            database_name=os.getenv("DB_NAME"), table_name=os.getenv("TABLE_NAME"),
                            username=os.getenv("DB_USERNAME"), password=os.getenv("DB_PASSWORD"))
    data = {
        "start_time": "07:35:00"
    }
    print(obj.patch_request(endpoint="update/3", data=data))
