# MultiDBAPI
A  powerful CRUD API for seamless interaction with multiple databases. Empowering developers with dynamic capabilities, MultiDBAPI streamlines the process of creating, reading, updating, and deleting data across multiple database.


# Set Up Guide
Install required packages from `requirements-latest.txt`

```
python3.9 =-m venv env
pip install -r requirements.txt
```


Add database information to .env file

```
# Database configurations
DB_ENGINE=postgresql+psycopg2
DB_HOST=localhost
DB_PORT="5432"

# Logging Configurations
LOG_FILE_ROTATION_INTERVAL=M


```
Runserver
```
uvicorn main:app --reload
```
# Dynamic API Url

|Method   	| Endpoint  	|Remarks   	
|---	|---	|---	
|POST   	|/schema    	            |Get Schema
|POST   	|/get    	            |Get All Data
|POST   	|/get?field_1=value    	|Get Data with query parameters
|POST   |/create    	            |Create New Entry
|PATCH  |/update{id} 	        |Update Existing Data
|DELETE   	|/delete?{id}         	|Delete Existing Data

## Request Body in JSON
- For all request user need to provide `database_info`
- For `/create` and `/update`, user need to provide necessary field value in `data` key.  
```
{
    {
    "database_info":{
        "database_name":"",
        "table_name":"",
        "username":"",
        "password":""
    },
    "data":{
        # provide field value ... 
    }
}
}
```