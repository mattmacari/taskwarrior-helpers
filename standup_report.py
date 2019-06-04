"""
standup_report
~~~~~~~~~~~~~~

Generates a standup report and writes it to stdout or a file.
"""
import os
import logging
from datetime import datetime, date
import typing
import operator

from dateutil.parser import parser
from dateutil.relativedelta import relativedelta
from taskw import TaskWarrior, task, TaskWarrior
from prettytable import PrettyTable

logger = logging.getLogger(__name__)


def get_completed_tasks(
    task_client: TaskWarrior, start_date: date, end_date: typing.Optional[date]
) -> typing.List[task.Task]:
    """
    Returns a list of completed tasks between a start and end date
    """
    ret_tasks = []
    logger.debug("Fetching list of completed tasks.")
    completed_tasks = task_client.load_tasks(command="completed").get(
        "completed"
    )  # type: typing.List[typing.Dict]
    for task in completed_tasks:
        # parse completed on
        completed_on = task.get("end")
        # completed on in window, then append
        if all([completed_on.date() >= start_date, completed_on.date() <= end_date]):
            ret_tasks.append(task)
    return sorted(ret_tasks, key=lambda x: operator.getitem(x, "end"))


def print_completed_tasks(completed_tasks: typing.Iterable[task.Task]):
    """
    Prints a list of completed tasks to the stdout
    """
    report_field_names = [
        "UUID",
        "Created",
        "Finished",
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
                str(task.get("uuid"))[:8],
                task.get("entry").date(),
                task.get("end").date(),
                task.get("project", " ").strip(),
                ",".join(task.get("tags", [])),
                task.get("description").strip(),
                task.get("jira", ""),
            ]
        )

    print(table)


def get_upcoming_tasks(
    task_client: TaskWarrior, due_date: date
) -> typing.List[task.Task]:
    """
    prints the tasks coming up due on the due_date
    """
    ret_tasks = []
    # grab tasks due on due_date
    tasks = task_client.load_tasks()["pending"]  # type: typing.List[typing.Dict]
    return [
        task for task in tasks if "due" in task and task.get("due").date() == due_date
    ]


def print_upcoming_tasks(upcoming_tasks: typing.Iterable[task.Task]):
    """
    Prints a list of upcoming tasks to the stdout
    """
    report_field_names = [
        "id",
        "UUID",
        "Priority",
        "Created",
        "Due",
        "Project",
        "tags",
        "Description",
        "JIRA Ticket",
    ]
    table = PrettyTable(field_names=report_field_names)
    table.align = "l"
    for task in upcoming_tasks:
        table.add_row(
            [
                task.get("id"),
                str(task.get("uuid"))[:8],
                task.get("priority", " "),
                task.get("entry").date(),
                task.get("due").date(),
                task.get("project", " ").strip(),
                ",".join(task.get("tags", [])),
                task.get("description").strip(),
                task.get("jira", ""),
            ]
        )

    print(table)


## print standup report

if __name__ == "__main__":
    # TODO: Wrap this in a main() method.
    task_client = TaskWarrior(marshal=True)
    today = date.today()
    yesterday = date.today() + relativedelta(days=-1)

    print(f"Daily Standup Report for {today}")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("")
    print("Yesterday's Completed Tasks")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("")
    completed_tasks = get_completed_tasks(
        task_client=task_client, start_date=yesterday, end_date=today
    )
    print_completed_tasks(completed_tasks)
    print("")
    print("Today's Tasks")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("")
    upcoming_tasks = get_upcoming_tasks(task_client=task_client, due_date=today)
    print_upcoming_tasks(upcoming_tasks)
