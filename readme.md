# Domain Monitoring Flask Application

This is a Flask-based web application designed to monitor the status of a list of domains. The application checks whether the domains are up, records their response time, HTTP status code, and IP address. It updates every 20 minutes and allows for manual triggering of the monitor. The application is secured with an access code to prevent unauthorized access.

## Features

- Monitors a list of domains and displays:
  - Domain status (UP/DOWN)
  - IP Address
  - Response time in seconds
  - HTTP Status code
  - Last checked time in Central Standard Time (CST)
- Real-time streaming of status updates via Server-Sent Events (SSE)
- Ability to manually trigger a domain check
- Access-protected with a custom code
- Logs all monitoring actions to both a file and console
- Uses background task scheduling with APScheduler to perform checks every 20 minutes

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/domain-monitor-flask.git
    cd domain-monitor-flask
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables for your Flask app:

    ```bash
    export FLASK_APP=app.py
    export FLASK_ENV=development
    ```

4. Modify the `ACCESS_CODE` in `app.py` with your desired access code:

    ```python
    ACCESS_CODE = "your_secret_code"
    ```

5. Run the application:

    ```bash
    flask run
    ```

6. The app will now be running at `http://localhost:5000`. Navigate there in your browser.

## How It Works

- **Domain Monitoring**: A list of predefined domains is monitored by the application. The domains are checked every 20 minutes to ensure their uptime and responsiveness. 
- **Manual Triggering**: Users can manually trigger the domain monitoring check through the web interface.
- **Security**: The app is protected by an access code. The user must enter the code on a login page before they can see the monitoring information.
- **Timezone Handling**: All timestamps in the application are converted to Central Standard Time (CST).
- **Background Scheduler**: The monitoring runs in the background using `APScheduler`, ensuring continuous checks even after user sessions.

## File Structure

```bash
.
├── app.py                # Main Flask application file
├── templates
│   ├── index.html        # Main domain monitor page
│   ├── login.html        # Login page template
├── domain_monitor.log     # Log file for domain checks
├── requirements.txt       # List of dependencies
└── README.md              # This readme file
```
## Requirements
- Flask
- APScheduler
- Requests
- pytz (for timezone handling)

Install the required dependencies using:

```bash
pip install -r requirements.txt
```

## Usage
1. Login: Navigate to http://localhost:5000/login and enter the access code to unlock the site.
2. View Domain Statuses: Once logged in, you can view the current statuses of the domains, including whether they're up, response times, IP addresses, and more.
3. Manual Monitor Trigger: Click "Run Monitor Now" to manually trigger a domain status check.
4. Automatic Monitoring: The domains are checked every 20 minutes automatically.

## Deployment
The app is designed to be deployed on platforms like Render or other cloud services that support Flask applications. Make sure to configure the necessary environment variables and set your ACCESS_CODE for secure access.

## Author
Erik Burdett

Email: erikaburdet@gmail.com / erik.burdett@andrewsama.com 
