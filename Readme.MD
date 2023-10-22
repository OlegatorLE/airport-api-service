# Airport API Service

Django Rest Framework project for managing Airport Service.
The project implements management of flights, planes, and crews. And the ability to create orders has also been implemented.

## Install via GitHub

Python3 must be already installed
```shell
    git clone https://github.com/OlegatorLE/airport-api-service.git
    cd airport-api-service
    python -m venv venv
    source venv/bin/activate # or venv\Scripts\activate in Windows
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
```

## JWT endpoints:
- create user:
  - api/user/register
- get access token:
  - api/user/token
- verify access token:
  - api/user/token/verify
- refresh token:
  - api/user/token/refresh
- manage user:
  - api/user/me

## Features

- Different accesses to APIRoot endpoint for anonymous and authorized users
- Admin panel /admin/
- Documentation at /api/doc/swagger
- Creating orders by auth users
- Creating airports by admins
- Creating airplanes with some type by admins
- Creating routes from source to destination by admins
- Adding flights with some routes and airplanes by admins
- Filtering airports by name, city or country
- Pagination airports and orders

## Demo
### Anonymous user APIRoot endpoint:

![anonym_api_root.png](https://github.com/OlegatorLE/airport-api-service/blob/develop/demo_images/anonym_api_root.png)

### Auth user APIRoot endpoint:

![auth_api_root.png](https://github.com/OlegatorLE/airport-api-service/blob/develop/demo_images/auth_api_root.png)

### Admin Airport-list endpoint:

![airport-list.png](https://github.com/OlegatorLE/airport-api-service/blob/develop/demo_images/airport-list.png)

### User Airport-detail endpoint:

![airport-detial.png](https://github.com/OlegatorLE/airport-api-service/blob/develop/demo_images/airport-detial.png)

### User Flight-list endpoint:

![flight-list.png](https://github.com/OlegatorLE/airport-api-service/blob/develop/demo_images/flight-list.png)

### User Flight-detail endpoint:

![flight-detail.png](https://github.com/OlegatorLE/airport-api-service/blob/develop/demo_images/flight-detail.png)

### Order-list endpoint:

![order-list.png](https://github.com/OlegatorLE/airport-api-service/blob/develop/demo_images/order-list.png)

### Order-detail endpoint:

![order-detail.png](https://github.com/OlegatorLE/airport-api-service/blob/develop/demo_images/order-detail.png)

### Admin page:

![admin-page.png](https://github.com/OlegatorLE/airport-api-service/blob/develop/demo_images/admin-page.png)
