# 🎅 Secret Santa

A Django project for managing employee Secret Santa assignments year-over-year with CSV upload support, previous history tracking, and automatic pairing generation.

---

## 🧰 Virtual Environment Setup

Before running the project, make sure to set up your Python virtual environment.

### Step 1: Install `virtualenv` (if not already installed)
```bash
pip install virtualenv

### Step 2: Create a virtual environment
```bash
python -m virtualenv demoEnv

### Step 3: Activate the virtual environment
```bash
demoEnv\Scripts\activate

## Install Project Dependencies

After activating your virtual environment, install all necessary packages:

```bash
pip install -r requirements.txt

This installs all dependencies used in the project including Django, pandas, etc.


## 🛠️ Database Setup

Before running the application, make sure your database is set up and credentials are configured in settings.py.

### Step 1: Create the database
Create a database (e.g., PostgreSQL, SQLite, etc.) and update the database settings in your Django settings.py.

### Step 2: Create migrations
```bash
python manage.py makemigrations

### Step 3: Apply migrations to create tables
```bash
python manage.py migrate

## 🚀 Run the Project
Start the development server:
```bash
python manage.py runserver

Then open this URL in your browser to access the landing screen:
```bash
http://127.0.0.1:8000/secret-santa/

## 📂 Project Scenarios

### 📁 Scenario 1: Upload Employee

This feature allows you to upload a new CSV file with employee details. The data will be stored in the database.

### 📁 Scenario 2: Upload Previous Secret-Santa Child

Upload a CSV containing last year’s Secret Santa assignments. If the data doesn't already exist in the database, it will be created.

### 🎲 Scenario 3: Generate Secret-Santa Child

Generates a new set of Secret Santa child assignments for the current year. The logic ensures:

No employee is assigned themselves

No repeat of previous year's assignment

Upon successful generation, the assignment will be available as a downloadable CSV file.