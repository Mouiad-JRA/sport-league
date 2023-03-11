# sport-league
## **Running the Project using Docker and Pipenv**

## Docker

### Steps


**1. Make sure Docker and Docker Compose installed on your machine.**

**2. Open the terminal and navigate to the project directory.**

**3. Build the Docker image by running the following command:**

    docker-compose build
**4. start the container by running the following command:**

    docker-compose up

**5. Now ,you can access the project in your browser by visiting**

    http://localhost:8000.
    

## Pipenv

### Steps

**1. install pipenv using the following command:**

    pip install pipenv
**2. Open the terminal and navigate to the project directory.**

**3. Activate the virtual environment using the following command:**

    pipenv shell

**4. Install the project dependencies by running the following command:**

    pipenv install
**5. migrate the database by running the following command:**

    python manage.py migrate
**6. start the server by running the following command:**

    python manage.py runserver
**7. Now, you can access the project in your browser by visiting** 

    http://localhost:8000.
