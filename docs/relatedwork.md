# Related Work

## National Grid Carbon Intensity App (UK)

website：https://www.neso.energy/

What it is: A real-time carbon intensity data visualization app.

How it works: Pulls live data from the National Grid and displays regional CO₂ intensity.

How my project differs:
- Goes beyond data display to offer actionable recommendations.
- Adds task scheduling and smart notifications.
- Designed for behavior change, not just monitoring.


## OhmConnect

Website: https://www.ohmconnect.com

What it is: A U.S. demand‑response platform that rewards residential users for reducing or shifting their electricity use during “Ohm Hours” (periods when the grid is under stress or there’s clean‑energy surplus).

How it works: Users link their utility meter via an API or smart‑meter integration. OhmConnect sends push/email alerts a few hours before an event. During the event window, users deliberately cut consumption (e.g. delay laundry). Participants earn points and cash rewards for hitting reduction targets.

How my project differs:
- Task Automation vs. Manual Alerts: Rather than just notifying users to “use less,” my app will let them pre‑schedule specific tasks (dishwasher, EV charging) to run automatically in low‑carbon windows.
- No Incentive Economy Required: My project focus purely on carbon‑aware scheduling, without needing a reward system or utility integration.
- Open‑Source & Extensible: Anyone can deploy my Python/Flask solution, modify the logic, and connect to any regional carbon API.

## WattTime

Website: https://watttime.org/

What it is: A nonprofit platform and API delivering real‑time marginal emissions data for U.S. power grids, aimed at utilities, device makers, and developers.

How it works: Publishes a REST/SDK interface with second‑by‑second marginal CO₂ emissions per balancing authority. Allows “automated emissions reduction” by letting connected devices shift loads when the grid is cleanest.

How my project differs:
- Consumer‑Friendly UI: My Flask app wraps similar data in an easy web dashboard for everyday users, not just developers.
- General‑Purpose Tasks: Beyond smart thermostats or industrial loads, your users can schedule any household appliance.
- Open‑Source Student Project: A simple Python/Flask stack that others can clone, adapt, or extend.

