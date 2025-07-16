# Related Work

## National Grid Carbon Intensity App (UK)

website：https://www.neso.energy/

What it is: A real-time carbon intensity data visualization app.

How it works: Pulls live data from the National Grid and displays regional CO₂ intensity.

How my project differs:
- Goes beyond data display to offer actionable recommendations.
- Adds task scheduling and smart notifications.
- Designed for behavior change, not just monitoring.


## ElectricityMaps

Website: https://app.electricitymaps.com/

What it is: A global real‑time carbon intensity dashboard showing power‑grid CO₂ levels on an interactive map.

How it works: Streams live data (via WebSockets) from multiple regional APIs. Color‑codes each region by its current carbon intensity. Lets you click a country or state to see a 48‑hour forecast and time‑series chart.

How my project differs:
- Personalized Recommendations: Instead of just maps, my app will pinpoint low‑carbon windows for each user’s tasks (e.g. laundry, EV charging).
- Task Scheduling & Reminders: Users can schedule appliances to run automatically at their chosen low‑carbon time and receive alerts.
- User Dashboard: Supports login, history tracking, and per‑user carbon‑saving stats.

## WattTime

Website: https://watttime.org/

What it is: A nonprofit platform and API delivering real‑time marginal emissions data for U.S. power grids, aimed at utilities, device makers, and developers.

How it works: Publishes a REST/SDK interface with second‑by‑second marginal CO₂ emissions per balancing authority. Allows “automated emissions reduction” by letting connected devices shift loads when the grid is cleanest.

How my project differs:
- Consumer‑Friendly UI: My Flask app wraps similar data in an easy web dashboard for everyday users, not just developers.
- General‑Purpose Tasks: Beyond smart thermostats or industrial loads, your users can schedule any household appliance.
- Open‑Source Student Project: A simple Python/Flask stack that others can clone, adapt, or extend.

