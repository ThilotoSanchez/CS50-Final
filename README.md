This CS50 2021 Final Project is dedicated to all people worldwide, working in healthcare and fighting the COVID-19 pandemic.

Our goal with the COVID Track webiste is to help people thinking about travelling, to get all important COVID-19 information about active, recovered & critical cases as well as numbers of deaths per country in one source. It should also spread hope about how many recovered and how we get back to the new normal.

The website is for educational purposes only. Thanks for API-sports for offering the COVID-19 API for free.

## Website structure
We build the site based on the Model-View-Controller (MVC) framework.

### Model
Our appliction uses an SQLite database to keep the data we receive via APIs and that we need in order to show it to the user and don't make too many API requests. We structured the API the following:

![db design](https://i.ibb.co/jJGsV41/db-design.png)

### View
On our website we use HTML, CSS and JavaScript to bring the page alive. Javascript is mostly used to show the charts on our index page. For the charts we use the Chart.js (see https://www.chartjs.org/). In CSS we defined some basic page settings. Nothing big. Notice some specifics for the index page to enable mobile users to have a better experience.

### Controller
We use Python as well as Flask in our app.py (which is the main application). Most functions have been excluded to the helpers.py file to keep the main application short & clean.

app.py: Our application uses Flask routes for the index, statistics, legal notice and data privacy pages. When the user is visiting the index page, it is showing statistics for the country based on the users IP address. If the users location isn't within one of the countries we have statistics for, the default is set to Switzerland. Those information are saved inside the session cookie.

helpers.py: Within the helpers file, we make all API requests to get the COVID data. The API we're using is provided by API-Sports (see https://rapidapi.com/api-sports/api/covid-193/). Thanks again! According to them, they use data from Google and Governmental pages. We make several calls to get the country history, current statistics but also all supported countries. We also use the file to write the data to our SQLite database. Helpers.py is also used for getting the data for the index Charts ready.

## Optional: Login, Logout and Register Function
We excluded the original basic Login, Logout and Register function but saved all code as well as the instructions in optional-login.txt. It's reused from what we learned earlier in CS50. It uses a nickname the user can select, a password with minimum requirements. The password is hashed and together with the nickname written in our SQlite database.

## Ideas to continue
- Use a Machine Learning algorithm to calculate the number of cases. This could give travellers a better feeling whether it could be safe to start their trip or better reschedule.
- Enable sorting for user on Statistics page.
- Include a Chloropeth World Map on the Statistics page to show the number of active covid cases.

## How-To: Install & start virtual environment on Windows
1. `python3 -m virtualenv env` will create virtual environment folder "env"
2. `env\Scripts\Activate.ps1` activates virtual environment (visible by (env) before path in terminal)

In order to see the Flask app locally, simply run `Flask run`.

We hope you like this Mini project. Feedback is always welcome.