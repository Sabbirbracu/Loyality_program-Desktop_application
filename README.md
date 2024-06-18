# Loyality_program-Desktop_application

This application is a customer loyalty program that allows you to manage customer points and purchases, and generate summaries of customer activities.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Features](#features)
- [Contact](#contact)

## Requirements

- Python 3.x
- MySQL

## Installation

### Step 1: Install Python

If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/) and run the installer. Make sure to check the option "Add Python to PATH" during installation.

### Step 2: Install MySQL

Download and install MySQL Community Server from [MySQL Community Downloads](https://dev.mysql.com/downloads/mysql/). Follow the setup instructions to install MySQL Server, MySQL Workbench, and other necessary components. Note down the MySQL root password you set during the installation.

### Step 3: Install Required Python Libraries

Open Command Prompt and run the following commands to install the required libraries:

```sh
pip install mysql-connector-python
pip install customtkinter
pip install tk
```

## Database Setup

### Step 1: Create the Database and Tables

Open MySQL Workbench or use the MySQL command line tool and run the following commands:

```sql
CREATE DATABASE loyalty_program;

USE loyalty_program;

CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    points FLOAT DEFAULT 0
);

CREATE TABLE purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    purchase_amount FLOAT,
    purchase_date DATETIME,
    Redeem_Points int,
    Get_Points int,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

## Running the Application

### Step 1: Download the Source Code

Save the provided Python code into a file named `loyalty_program.py`.

### Step 2: Run the Script

Open Command Prompt, navigate to the directory where `loyalty_program.py` is saved, and run the script with the following command:

```sh
python loyalty_program.py
```

## Features

- **Customer Account Management**: Create and manage customer accounts with phone numbers and names.
- **Purchase and Points Management**: Record purchases and manage customer points.
- **Redeem Points**: Redeem points during purchases.
- **Sell Summary**: View and search sell summaries within specified date ranges.
- **Customer Summary**: View customer-specific summaries.
- **CSV Export**: Export sell and customer summaries to CSV files.
- **User Interface**: User-friendly interface built with CustomTkinter.

## Contact

For any questions or support, please contact us at: [sabbirahmad653@gmail.com](mailto:sabbirahmad653@gmail.com).
