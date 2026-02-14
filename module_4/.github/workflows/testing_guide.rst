Testing Guide
=============

Running Tests
-------------

.. code-block:: bash

   pytest -m "web or buttons or analysis or db or integration"

Markers
-------

- ``web`` — Flask page rendering
- ``buttons`` — pull/update behavior
- ``analysis`` — formatting and labels
- ``db`` — database writes and schema
- ``integration`` — end-to-end flows

Fixtures
--------

The test suite uses:

- Flask test client
- Mocked scraper/cleaner/loader
- Temporary PostgreSQL database (via DATABASE_URL)
