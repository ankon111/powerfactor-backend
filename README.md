# POWERFACTOR BACKEND

Welcome to PowerFactor Backend Project.

### Source Code
Please install git and clone the source code by running following command from your terminal:
```
git clone 
```

**Note:** If you see I provided `.env` in the git repository which is not ideal, Usually we should provide `
.env_template` file and who will run the source will create his own `.env` based on that template. However, to make 
things easy and run the source quickly I provided `.env` in the git repository.

### Environment

Please install docker from this [link](https://docs.docker.com/get-docker/). For interaction with API I used postman, 
you can install it from [here](https://www.postman.com/downloads/). That's it you are all set. 

### RUN

Please run the following command to light up all the services:

```
docker-compose up -d --build
```

We need to run the migration script by ourselves. This can be done using some script as well but this about that if we 
use some script which will run everytime when the container starts up, that would be unnecessary. That's why we keep 
this command controls in our hand. Run the following command to make necessary changes in the database: 

```
docker-compose exec web python manage.py migrate
```

To observe the logs of any service we can use following command:

```
docker-compose logs <service-name>
```

Example run `docker-compose logs web` to see the web service/ django app logs.

### Explore With Postman

Inorder to interact with API I have shared a postman file [here](solar-plant-app.postman_collection.json), you can 
simply import this file into postman and checkout the api. Here is brief description of different endpoints:
* solar-plant(CRUD)
  * /api/solar-plant/ 
    * POST - Create solar plant 
    * GET  - List of solar plant
  * /api/solar-plant/plant/<int: plant_id>
    * GET  - Fetch specific plant info by plant id
    * PUT  - Update plant name by plant id
    * DEL  - Delete specific plant by plant id
  * /api/solar-plant/data/?plant-id=<plant_id>&from=<from_date>&to=<to_date>
    * GET  - Fetch raw data from the backend service within this date range
  * /api/solar-plant/report/?plant-id=<plant_id>&from=<from_date>&to=<to_date>
    * GET  - Fetch hourly sum of all fields from the backend service within this date range

### API Testing

I have written few test cases for API views. In order to run the tests we need to run the following command:

```
docker-compose exec web python manage.py test
```

### Periodic Task

Sync Database periodic task. Details of the database sync is given below:

The database is synced (task is triggered) in one of two ways:

  1. Once a solar plant id is created
        * If the sync is triggered by plant id creation then we will sync the data
        only for the specific plant that is just created. First we sync for immediate date,
        which is yesterday's data and then we sync the database for one or more years based on
        the `SYNC_EVERY_RUN` param. e.g if SYNC_EVERY_RUN is 2 then this will sync two years of data
        from the oldest date that exist for specific that plant id. How many years of previous data
        we will save in our backend that is also parameterized by `SYNC_UNTIL_YEAR`
  2. In a daily interval (periodic task,)
        * For periodic task all the logics are same except this runs for all plants.
        * For demonstration, I run the cronjob in every 20 mins 

**Note:** Monitoring service requests are wrapped by retry mechanism, as monitoring service sometimes become 
unavailable.

### FutureTask:
* We covered our code with few tests, more test coverage should be done.
* Add a CI/CD pipeline which will check the testing automatically, and if tests passed then deploy in the server.
* flake8 is used for linting but for now we need to run it by ourselves/manually. We should configure with pre-commit 
hook so that the coding style will conform every time we will commit something.