Instruction on how to export your automated tests to xml and then import it in Qase Test case management software.
1. Run pytest in verbose mode on your test suite and write it to file. Example:
pytest -v parse_datetime_test.py > output.txt
2. Run export_tests.py main, passing to export_to_xml input and output files and all needed test suite data. Example:
export_to_xml('output.txt', 'wb_parse_datetime.xml', 'WB: khal.parse_datetime',
                  'White box tests for module khal.parse_datetime',
                  'Khal sources should be intact and there should exist version.py file. '
                  'You should install `pytest` and `coverage` Python packages.')
3. Go to your Qase project and import your xml. In our example you should import `wb_parse_datetime.xml`.