# Finance Manager

Finance Manager is a web-based personal finance management application developed using Python, Flask, and SQLAlchemy. The application helps users efficiently manage their finances by tracking accounts, recording transactions, categorizing expenses, and monitoring spending patterns through an intuitive user interface.

The project follows a modular architecture and utilizes SQLAlchemy ORM for database management, Flask-Login for authentication, and Alembic for database migrations.

---

## Features

* User Registration and Authentication
* Secure Login and Logout Functionality
* Account Management
* Income and Expense Tracking
* Transaction Categorization
* Password Recovery via Email
* Database Migration Support
* User Profile Management
* Responsive Web Interface

---

## Tech Stack

### Backend

* Python
* Flask

### Database

* SQLite
* SQLAlchemy ORM

### Authentication

* Flask-Login

### Database Migration

* Flask-Migrate
* Alembic

### Frontend

* HTML
* CSS
* Bootstrap

### Additional Services

* Flask-Mail

---

## Database Model

The application consists of four primary entities:

### User

Stores user profile information and authentication details.

### Account

Represents financial accounts belonging to a user.

### Transaction

Stores income and expense records associated with an account.

### Category

Used to classify transactions into different spending and income categories.

The relationships between these entities ensure structured and efficient financial data management.

![Database Model](pics/DB%20Model%2020200212_v1.PNG)

---

## Application Screenshots

### User Profile

![User Profile](pics/user_profile.PNG)

### Account Overview

![Account Overview](pics/account_overview.PNG)

### Add Transaction

![Add Transaction](pics/add_transaction50.png)

### Login Page

![Login Page](pics/login_page50.png)

### Password Recovery Email

![Password Recovery Email](pics/password_recovery_email.PNG)

---

## Project Architecture

The application is built using Flask's Blueprint architecture and follows a modular design pattern. SQLAlchemy ORM is used for database interaction, while Flask-Login manages user authentication and session handling.

Database schema changes are managed through Alembic migrations, allowing seamless updates and version control of database structures.

---

## Objectives

* Simplify personal finance management
* Track income and expenses effectively
* Organize financial data using categories
* Provide secure user authentication
* Demonstrate full-stack web development using Flask

---

## Future Enhancements

* Bank Account Integration
* RESTful API with JSON Responses
* JavaScript / React Frontend
* Interactive Dashboard and Analytics
* Budget Planning and Expense Forecasting
* Data Visualization using Charts and Graphs
* Export Financial Reports in PDF/Excel Format

---

## Installation

```bash
git clone <repository-url>
cd Finance-Manager

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python finmgr.py
```

---

## License

This project was developed for learning and educational purposes and demonstrates the implementation of a finance management system using Flask and SQLAlchemy.
