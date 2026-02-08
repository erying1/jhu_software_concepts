echo '========================================'
echo ' JHU Software Concepts — Full Pipeline '
echo '========================================'

echo ''
echo 'Step 1: Running scraper (Module 2.1)...'
echo '----------------------------------------'
python module_3/module_2.1/scrape.py

echo ''
echo 'Step 2: Running cleaner (Module 2.1)...'
echo '----------------------------------------'
python module_3/module_2.1/clean.py

echo ''
echo 'Step 3: Loading cleaned data into PostgreSQL (Module 3)...'
echo '----------------------------------------'
python module_3/load_data.py --drop

echo ''
echo 'Step 4: Starting Flask dashboard (Module 3)...'
echo '----------------------------------------'
python module_3/run.py
