Theatre-API-Service
A Django REST Framework (DRF) based API service for theatre management.

Installation from GitHub

1. Install PostgreSQL and create a database.

2. Clone the repository:

``git clone https://github.com/olga-kim7/Theatre-API-Service.git`` 

``cd Theatre-API-Service``

3. Set up a virtual environment and activate it:

``python -m venv venv``

``source venv/bin/activate  # On Windows use `venv\Scripts\activate``

4. Install dependencies:

`pip install -r requirements.txt`

5. Set environment variables:

``export DB_HOST=<your_db_hostname>``

``export DB_NAME=<your_db_name>``

``export DB_USER=<your_db_username>``

``export DB_PASSWORD=<your_db_password>``

``export SECRET_KEY=<your_secret_key>``

6. Apply migrations and run the server:

``python manage.py migrate``

``python manage.py runserver``

Running with Docker
Ensure Docker is installed on your system.

1. Build Docker containers:
`docker-compose build`
2. Start Docker containers:
`docker-compose up`

Accessing the API

1. Create a user:
`POST /api/user/register/`
2. Obtain an access token:
`POST /api/user/token/`

Features:
1. JFT authenticated
2. Admin panel /admin/
3. Documentations is located at /api/doc/swagger
4. Managing reservation and tickets
6. Creating full plays with actors, genres
7. Create theatre halls
8. Adding performances
7. Filtering plays and performances