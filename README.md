# Calculate your Transit Tax Deduction Amount

## To use:

1.  Log into your <a href="https://www.compasscard.ca/">compass account</a>
2.  Download all transactions from your desired tax year.  At the time of writing, Compass permitted a maximum 90 day period for downloading your usage history so you'll have to do this a few times to get the whole year.
3.  Move all the csv files you downloaded to the '/data' folder.

The filter on the compass website might still be a bit wonky, so don't worry if you get some duplicate dates, or entries with dates outside the tax year you want.  These anomalies are taken care of.

4.  From command line, run the cmp_viz.py script in Python 3.5+
    (<a href="https://www.python.org/about/gettingstarted/">What's Python?  How do I get it?</a>)

5.  The printed output should tell you your eligible transit usage date range, and the total value spent in that time period, which *if the code is correct* corresponds to the Deduction Amount.

6.  If you're really keen, improve the code (it's really bad, yeah.), documentation, or functionality.

7.  If you're a hero to all those good folks who do public service by using transit and not contributing to traffic, make it into a publicly available, free web app!

## License & Disclaimer
The author does not guarantee accuracy of the information provided.  Use at your own peril.

## License

<a href="https://creativecommons.org/licenses/by-nc/2.0/ca/">Attribution-NonCommercial 2.0 Canada (CC BY-NC 2.0 CA)</a>
