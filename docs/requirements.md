# User Requirements

## Functional Requirements

Must Have 

1. User Registration & Login
Implement user authentication using Flask-Login for session management and Flask-WTF for secure form handling.
Securely hash passwords using bcrypt and store user credentials securely in a SQLite database.
Offer a “Remember Me” option via persistent sessions handled by Flask-Login, ensuring secure user convenience.

2. Real-Time Carbon Intensity Display
Use Python Flask backend to fetch live data from the UK Carbon Intensity API at regular intervals (every 30 mins) via RESTful requests (requests library).
Cache recent API responses briefly using Flask’s caching mechanisms or an in-memory cache to ensure resilience to API downtime.
Display the real-time carbon intensity clearly on the frontend dashboard using HTML/CSS/JavaScript, styled with Bootstrap for responsiveness.

3. Optimal Electricity Usage Recommendations
Develop a backend algorithm in Python (Flask) to analyze real-time carbon intensity data, identifying low-carbon time slots.
Clearly present recommendations on the frontend dashboard using color-coded indicators built with HTML/CSS, enhanced by JavaScript interactivity.

Should Have

4. Task Scheduling for Energy-Intensive Activities
Allow users to schedule tasks like laundry or EV charging through intuitive HTML forms styled with Bootstrap.
Store scheduled tasks securely in a SQLite database, managing task persistence with Flask SQLAlchemy ORM.
Use APScheduler (Python scheduling library) to automate task notifications and scheduled reminders in the backend, ensuring timely user prompts.

5. Dashboard View with Historical Graphs and User Habits
Record historical carbon intensity data and user activities in a structured SQLite database.
Render interactive visualizations of historical and user-specific data on the frontend using JavaScript with Chart.js, embedded into HTML pages styled by Bootstrap.

Could Have

6. User Reminders and Notifications
Implement web-based notifications using JavaScript’s Web Notification API to remind users of upcoming tasks or optimal usage windows.
For email notifications, use SMTP integration in Flask (e.g., via Flask-Mail) to deliver reminders, managed in the backend with scheduled tasks (APScheduler).

Would Like to Have

7. Enhanced User Analytics and Insights
Utilize Python analytics libraries (Pandas, scikit-learn) on Flask backend to analyze and predict user electricity usage patterns.
Generate personalized insights, displayed as enhanced visualizations (e.g., predictive charts via Chart.js), providing actionable analytics to further reduce carbon footprints.

## Non-Functional Requirements

1. Security:
Encrypt user credentials using bcrypt hashing via Flask security libraries.
Enforce secure HTTPS connections through hosting providers (Render or Railway).
Secure form submission and validation with Flask-WTF.

2. Reliability:
Implement caching and error-handling strategies within Flask to gracefully manage external API downtime.
Ensure backend robustness through scheduled backups or data snapshots.

3.Version Control:
Use GitHub for version control, tracking all code changes, documentation, and collaboration via clear branching and issue management.
Deployment:
Deploy the Flask application efficiently and securely using platform-as-a-service providers (Render or Railway), streamlining continuous integration and deployment processes.

4.Usability:
Leverage Bootstrap to ensure responsive, intuitive UI designs that are user-friendly, even for non-technical audiences.
Provide clear documentation and helpful guidance within the interface to ensure smooth user adoption.


