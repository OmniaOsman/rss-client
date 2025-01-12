# RSS Client

## Overview

The RSS Client is a web application designed to help users manage and stay updated with their favorite news sources. The application allows users to create groups, add sources to these groups, and fetch the latest news articles. Users can also subscribe to a newsletter to receive regular updates via email.

## Features

- **User Authentication**: Secure login and logout functionality.
- **UID Display**: Display each user's unique identifier (UID) (will need it for the URL to be added to any RSS feed app to get the summary).
- **Group Management**: Create, view, and delete groups.
- **Source Management**: Add, view, and delete sources within groups.
- **News Summary**: Fetch and display a summary of the latest news articles.
- **Newsletter Subscription**: Subscribe or unsubscribe from the newsletter.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Django, Django REST framework
- **Database**: Postgres
- **Authentication**: Token-based authentication
- **API**: RESTful API for managing groups, sources, and news articles

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/OmniaOsman/rss-client.git
    cd rss-client
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Apply migrations**:
    ```bash
    python manage.py migrate
    ```

5. **Run the development server**:
    ```bash
    python manage.py runserver
    ```

6. **Access the application**:
    Open your web browser and navigate to `http://localhost:8000`.

## Usage

1. **Sign Up / Sign In**: Create an account or sign in with existing credentials.
2. **Create Groups**: Add new groups to categorize your news sources.
3. **Add Sources**: Add RSS feed URLs to your groups.
4. **Fetch News**: Click on "تحديث اﻷخبار" to fetch the latest news articles.
5. **View News Summary**: Click on "ملخص الأخبار" to view a summary of the latest news articles.
6. **Subscribe to Newsletter**: Use the "نعم" and "لا" buttons to subscribe or unsubscribe from the newsletter.
7. **Logout**: Click on "تسجيل الخروج" to log out of the application.


