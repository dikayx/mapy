# Testing

If you want to contribute to the project, you can run the tests to make sure everything is working as expected. The tests are located in the `tests` directory and cover the main functionality of the app. Unit testing is done using `pytest`.

There are three main types of tests (as of now):

1. **Web tests**: These tests check the main functionality of the website, mainly the proper routing and rendering of the pages. They use the `pytest` library to simulate HTTP requests and check the responses.

2. **Utils tests**: These tests check the utility functions used in the app, such as parsing EXIF data and generating Google Maps links. They also mock image files to check the behavior of the functions.

3. **Helpers tests**: These tests check the helper functions used in the app, such as handling only certain file types.

New tests can be added to the `tests` directory following the same structure as the existing tests. I welcome any contributions to the test suite to improve the overall quality of the app.

## Running the tests

You can run the tests using the following command in the root directory of the project:

```bash
pytest
```

This will run all the tests in the `tests` directory and output the results in the terminal. If all tests pass, you should see a message indicating that all tests have passed successfully.

That's it! You are now ready to contribute to the project by adding new features, fixing bugs, or improving the existing codebase. If you have any questions or need help with anything, feel free to [open an issue](https://github.com/dan-koller/mapy/issues) or reach out to me directly.

## Coverage

Currently, the test coverage of the project is around 90%. This means that 90% of the codebase is covered by the tests. To check the test coverage of the project, you can run the following command:

```bash
pytest --cov=mapy tests/
```

This results in an output like this:

```
---------- coverage: platform darwin, python 3.12.4-final-0 ----------
Name                         Stmts   Miss  Cover
------------------------------------------------
mapy/__init__.py                 0      0   100%
mapy/app.py                     21      0   100%
mapy/context_processors.py      21      5    76%
mapy/routes.py                  16      2    88%
mapy/utils.py                  192     17    91%
------------------------------------------------
TOTAL                          250     24    90%
```
