"""
standup_report
~~~~~~~~~~~~~~

Generates a standup report and writes it to stdout or a file.
"""
import os
import logging
from datetime import datetime, date
import typing

from dateutil.parser import parser
from dateutil.relativedelta import relativedelta
from taskw import TaskWarrior, task
from prettytable import PrettyTable


def get_completed_tasks(
    task_client: TaskWarrior, start_date: date, end_date: typing.Optional[date]
) -> typing.List[task.Task]:
    """
    Returns a list of completed tasks between a start and end date
    """
    ret_tasks = []
    logging.debug("Fetching list of completed tasks.")
    completed_tasks = task_client.load_tasks(command="completed").get(
        "completed"
    )  # typing.List[typing.Dict]
    date_parser = parser()
    for task in completed_tasks:
        # parse completed on
        completed_on = date_parser.parse(timestr=task.get("end"))
        # completed on in window, then append
        if all([completed_on.date() >= start_date, completed_on.date() <= end_date]):
            ret_tasks.append(task)
    return ret_tasks


def print_completed_tasks(completed_tasks: typing.Iterable[task.Task]):
    """
    Prints a list of completed tasks to the stdout
    """
    date_parser = parser()
    report_field_names = [
        "UUID",
        "Created",
        "Project",
        "tags",
        "Description",
        "JIRA Ticket",
    ]
    table = PrettyTable(field_names=report_field_names)
    table.align = "l"
    for task in completed_tasks:
        table.add_row(
            [
                task.get("uuid")[:8],
                date_parser.parse(timestr=task.get("entry")).date(),
                task.get("project", "").strip(),
                ",".join(task.get("tags", [])),
                task.get("description").strip(),
                task.get("jira", ""),
            ]
        )

    print(table)


def upcoming_tasks(task_client: TaskWarrior, due_date: date) -> typing.List[task.Task]:
    pass


## print standup report

if __name__ == "__main__":

    task_client = TaskWarrior()
    today = date.today()
    yesterday = date.today() + relativedelta(days=-1)
    print(f"Daily Standup Report for {today}")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("")
    print("Yesterday's Completed Tasks")
    print("")
    completed_tasks = get_completed_tasks(
        task_client=task_client, start_date=yesterday, end_date=today
    )
    print_completed_tasks(completed_tasks)

    print("Today's Tasks")
    print("")
