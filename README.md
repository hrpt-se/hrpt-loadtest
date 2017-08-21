# HRPT-loadtest
This test is intended to test how the HRPT site work under load, with focus on testing the survey system.

## Requirements
  * Python with Pip
  * (Optional) Virtualenv

## Installing
  1. Clone the repo and enter the directory. `git clone https://github.com/hrpt-se/hrpt-loadtest.git && cd hrpt-loadtest`
  2. (optional) Create and activate a new virtualenv: `virtualenv venv && . venv/bin/activate`
  3. Install the requirements `pip install -r requirements.txt`

## Running
  1. Start the test daemon: `locust --host <server url>`
  2. Go to the load testing tool, running on `http://localhost:8090` and run the test suite.

## Configuration
The following parameters control how the test is carried out.

In `locustfile.py`:
  * `min_wait` The minimum time between two requests for a simulated users
  * `max_wait` The maximum time between two requests for a simulated users
  
In the load testing tool:
  * `clients` The number of clients running concurrently
  * `hatch_rate` The number of new simulated users that should connect per second.
