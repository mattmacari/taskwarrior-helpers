"""
standup_report
~~~~~~~~~~~~~~

Generates a standup report and writes it to stdout or a file.
"""
import logging
import operator
import os
import typing
from datetime import date, datetime

from dateutil.parser import parser
from dateutil.relativedelta import relativedelta, SA
from prettytable import PrettyTable
from taskw import TaskWarrior, task
from taskw.warrior import Status

logger = logging.getLogger(__name__)


def get_completed_tasks(
    task_client: TaskWarrior, start_date: date, end_date: typing.Optional[date]
) -> typing.List[task.Task]:
    """
    Returns a list of completed tasks between a start and end date
    """
    ret_tasks = []
    logger.debug("Fetching list of completed tasks.")
    completed_tasks = task_client.filter_tasks(
        filter_dict={"status": Status.COMPLETED}
    )  # type: typing.List[typing.Dict]
    for task in completed_tasks:
        # parse completed on
        completed_on = task.get("end")
        # completed on in window, then append
        if all([completed_on.date() >= start_date, completed_on.date() <= end_date]):
            ret_tasks.append(task)
    return sorted(ret_tasks, key=lambda x: operator.getitem(x, "end"))


def get_tasks_by_due_date(
    task_client: TaskWarrior, due_date: date
) -> typing.List[task.Task]:
    """
    prints the tasks coming up due on the due_date
    """
    # grab tasks due on due_date
    tasks = task_client.filter_tasks(
        filter_dict={"status": Status.PENDING}
    )  # type: typing.List[typing.Dict]
    return [
        task for task in tasks if "due" in task and task.get("due").date() == due_date
    ]


def filter_tasks(
    task_client: TaskWarrior,
    filter_callable: typing.Callable,
    status: str = Status.PENDING,
) -> typing.List[task.Task]:
    """
    Filters the tasks based on the callable passed in.
    """
    tasks = task_client.filter_tasks(filter_dict={"status": status})
    return sorted(
        (task for task in tasks if filter_callable(task)),
        key=lambda x: operator.getitem(x, "urgency"),
        reverse=True,
    )


def print_task_table(tasks: typing.Iterable[task.Task]):
    """
    Prints a list of upcoming tasks to the stdout
    """
    report_field_names = [
        "id",
        "UUID",
        "Priority",
        "Urgency",
        "Created",
        "Due",
        "Done",
        "Project",
        "tags",
        "Description",
        "JIRA Ticket",
    ]
    table = PrettyTable(field_names=report_field_names)
    table.align = "l"
    for task in tasks:
        table.add_row(
            [
                task.get("id"),
                str(task.get("uuid"))[:8],
                task.get("priority", " "),
                task.get("urgency"),
                task.get("entry").date(),
                task.get("due").date() if task.get("due") else "",
                task.get("end").date() if task.get("end") else "",
                task.get("project", " ").strip(),
                ",".join(task.get("tags", [])),
                task.get("description").strip(),
                task.get("jira", ""),
            ]
        )

    print(table)


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
    print_task_table(completed_tasks)

    overdue_tasks = filter_tasks(
        task_client=task_client,
        filter_callable=lambda x: "due" in x and x.get("due").date() < date.today(),
        status=Status.PENDING,
    )
    if overdue_tasks:
        print("")
        print("Overdue tasks")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")
        print_task_table(overdue_tasks)

    print("")
    print("Today's Tasks")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("")
    tasks_due_today = filter_tasks(
        task_client=task_client,
        filter_callable=lambda x: "due" in x and x.get("due").date() == date.today(),
        status=Status.PENDING,
    )
    print_task_table(tasks_due_today)

    print("")
    print("This Week's Tasks (Due by Saturday)")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("")
    saturday_dt = date.today() + relativedelta(days=1, weekday=SA)
    tasks_due_by_saturday = filter_tasks(
        task_client=task_client,
        filter_callable=lambda x: "due" in x
        and x.get("due").date() <= saturday_dt
        and x.get("due").date() > date.today(),
        status=Status.PENDING,
    )
    print_task_table(tasks_due_by_saturday)
