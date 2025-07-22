# User Requirements

## Functional Requirements

Must Have 

1. User Registration & Login
Users will securely register and log in using credentials managed by Flask-Login and Flask-WTF for form validation and security. Passwords will be hashed and securely stored in an SQLite database using bcrypt. Users will have a "Remember Me" option via persistent sessions. Optionally, OAuth (OpenID Connect) integration may be implemented, allowing users to authenticate securely through trusted third-party services (Google, GitHub) and reducing the need to store passwords locally.

2. Real-Time Carbon Intensity Display
Real-time data fetched from the UK Carbon Intensity API by the Python Flask backend will be cached and periodically refreshed every 30 minutes to ensure reliability. The frontend, developed with HTML/CSS, JavaScript, and Bootstrap for responsive design, will dynamically present live carbon intensity data clearly through an intuitive Line Chart powered by Chart.js, allowing users to instantly understand the current carbon intensity levels and trends.

3. Optimal Electricity Usage Recommendations
Recommendations for optimal electricity usage will be derived from the Flask backend’s analysis of live carbon intensity data. Recommended low-carbon periods will be clearly presented on the dashboard using intuitive, color-coded visuals, such as a Heatmap or Bar Chart implemented via Chart.js. Users can quickly identify the most environmentally friendly times for using electricity.

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

5. Deployment:
Application deployment on a managed hosting platform (Render or Railway), simplifying continuous integration, deployment, and scalability.

