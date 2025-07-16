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

## Octopus Energy EV Smart Charging

Website: https://octopus.energy/ev-charging/

What it is: Octopus Energy’s customer portal for smart EV charging, combining their Agile tariff (half‑hourly price signals) with carbon forecasts to optimize vehicle charging.

How it works: Pulls Agile price data + National Grid carbon intensity forecasts. Users set desired charge level and by-when deadline. The system automatically schedules charging to hit targets during the cheapest/cleanest windows.

How my project differs:
- Broader Appliance Coverage: My tool isn’t limited to EVs—you’ll let users schedule any appliance or task.
- Multi‑Task Scheduling: Users can queue multiple tasks (washing, charging, battery backup) with individual preferences.
- No Vendor Lock‑In: Works for anyone with a browser and account, regardless of energy supplier.


