My Money Forecast
=================

My Money Forecast is an easy-to-use budget forecaster. It gives you an instant overview of your monthly expenses from the
current month on, enabling you to plan your finances ahead. It also supports multiple users, isolating the data and providing total privacy for you and your family members.

You don't have to be an accounter to know how much you are spending or saving!

This project is made with Django and served under UNLICENSE, so it can be used by anyone, for commercial and non-commerical purposes. 

Beware that as we use third-party tools, their license must be respected accordingly. This software is free to use and to distribute, improvements are also welcome!
 
![screenshot of work so far](http://www.andersonsantos.info/img/money_forecast_.png)

To install, simply download, install the requirements.txt using pip and run the application as a normal django site.

Tests are written in py.test and can be run directly under the moneyforecast django project folder.

TODO:

- Improve performance on calculating the grid
- Refactor month_control module, it's overdoing things
- SAVINGS, UNSCHEDULED records workflow need improvement
- Review translations
- Display Budget in the Outcome popup list
- Make Budget editable from the dashboard
- CSV importer of records
- Other improvements are not planned or not well defined