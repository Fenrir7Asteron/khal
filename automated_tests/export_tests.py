# -*- coding: utf-8 -*-
import xml.etree.ElementTree as xml
import csv


def export_to_xml(input_file: str, output_file: str, suite: str,
                  suite_description_: str = '', suite_preconditions_: str = '', parent_suite_: str = ''):
    nodes = xml.Element("nodes")
    suites = xml.SubElement(nodes, "suites")
    node = xml.SubElement(suites, "node")

    suite_id = xml.SubElement(node, "id")
    suite_id.text = "1"
    suite_title = xml.SubElement(node, "title")
    suite_title.text = suite
    suite_description = xml.SubElement(node, "description")
    suite_description.text = suite_description_
    suite_preconditions = xml.SubElement(node, "preconditions")
    suite_preconditions.text = suite_preconditions_
    parent_suite = xml.SubElement(node, "suites")
    parent_suite.text = parent_suite_

    cases = xml.SubElement(node, "cases")

    with open(input_file, "r") as inp:
        lines = inp.readlines()
        lines = list(filter(lambda line: '::' in line and '%' in line, lines))

        i = 1
        for line in lines:
            clss = line[line.find('::') + 2:line.rfind('::')]
            method = line[line.rfind('::') + 2:line.find(' ')]

            case = xml.SubElement(cases, "node")
            id = xml.SubElement(case, "id")
            id.text = str(i)
            title = xml.SubElement(case, "title")
            title.text = clss + ': ' + method
            description = xml.SubElement(case, "description")
            description.text = ''
            preconditions = xml.SubElement(case, "preconditions")
            preconditions.text = ''
            postconditions = xml.SubElement(case, "postconditions")
            postconditions.text = 'Test should pass leaving no side effects.'
            priority = xml.SubElement(case, "priority")
            priority.text = 'medium'
            severity = xml.SubElement(case, "severity")
            severity.text = 'medium'
            behavior = xml.SubElement(case, "behavior")
            behavior.text = 'undefined'
            type = xml.SubElement(case, "type")
            type.text = 'other'
            automation = xml.SubElement(case, "automation")
            automation.text = 'automated'
            status = xml.SubElement(case, "status")
            status.text = 'actual'
            milestone = xml.SubElement(case, "milestone")
            custom_fields = xml.SubElement(case, "custom_fields")
            steps = xml.SubElement(case, "steps")

            step = xml.SubElement(steps, "node")
            position = xml.SubElement(step, "position")
            position.text = "1"
            action = xml.SubElement(step, "action")
            action.text = 'Run test suite from the terminal\ncoverage run ' \
                          '--branch --source=khal.parse_datetime -m pytest automated_tests/parse_datetime_test.py '
            expected_result = xml.SubElement(step, "expected_result")
            expected_result.text = 'Test should PASS.'
            data = xml.SubElement(step, "data")

            i += 1

    tree = xml.ElementTree(nodes)
    tree.write(output_file)


def export_to_csv(input_file, output_file, suite):
    with open(input_file, "r") as inp:
        lines = inp.readlines()
        lines = list(filter(lambda line: '::' in line and '%' in line, lines))

        id = 1
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['id', 'title', 'description', 'preconditions', 'postconditions', 'priority', 'severity',
                             'type', 'behavior', 'automation', 'status', 'steps_actions', 'steps_result', 'suite'])
        for line in lines:
            clss = line[line.find('::') + 2:line.rfind('::')]
            method = line[line.rfind('::') + 2:line.find(' ')]

            with open(output_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                title = clss + ': ' + method
                description = ''
                preconditions = ''
                postconditions = 'Test should pass leaving no side effects.'
                priority = 'medium'
                severity = 'medium'
                type = 'other'
                behavior = 'undefined'
                automation = 'automated'
                status = 'actual'
                steps_actions = '1. Run test suite from the terminal\ncoverage run ' \
                                '--branch --source=khal.parse_datetime -m pytest automated_tests/parse_datetime_test.py '
                steps_result = '1. Test should PASS.'
                suite = ''
                writer.writerow([id, title, description, preconditions, postconditions, priority, severity, type,
                                 behavior, automation, status, steps_actions, steps_result, suite])
                id += 1


if __name__ == '__main__':
    export_to_xml('output.txt', 'wb_calendar_display.xml', 'WB: khal.calendar_display',
                  'White box tests for module khal.calendar_display',
                  'Khal sources should be intact and there should exist version.py file. '
                  'You should install `pytest` and `coverage` Python packages.')
