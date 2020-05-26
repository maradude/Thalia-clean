# End to end testing with Selenium

## Notes on running tests

Due to limitations of architecture and CircleCI, end-to-end tests with Selenium must be run locally. To run tests Thalia must be installed locally and available at localhost:5000. In addition selenium must be configured for use with both the Chrome and Firefox web drivers (chromedriver and geckodriver must be installed in the system PATH) and have the prototype financial data database installed. 

Some issues may arise due when run on a particularly slow system (most likely driver address checks will fail). To counteract this increase the `page_wait` time in `util.py`.

Tests can be run individually by running the appropriate python scripts. If run individually the webdriver/s will not run in headless mode. This is done for easy debugging. To run all tests on both drivers run the `main_test.py` script.
