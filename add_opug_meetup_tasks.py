"""
add_opug_meetup_tasks.py
~~~~~~~~~~~~~~~~~~~~~~~~

Simple utility script to create tasks I need to to the month prior to an OPUG meeting.

"""
import calendar
import logging
import os
import typing
from datetime import date, datetime

import click
from dateutil.parser import parser
from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable
from taskw import TaskWarrior, task

logger = logging.getLogger(__name__)

DEFAULT_TAGS = ["opug"]
DEFAULT_PRIORITY = "M"


class MeetupTask(typing.NamedTuple):
    description: str
    date_offset: typing.Dict[str, int]


TASK_LIST = [
    # before meetup
    MeetupTask("verify topics with presenters", {"weeks": -3}),
    MeetupTask("update meetup with topics/abstracts", {"weeks": -2}),
    MeetupTask("tweet from opug twitter about upcoming meeting", {"weeks": -2}),
    MeetupTask("tweet from opug twitter about upcoming meeting", {"weeks": -1}),
    MeetupTask("tweet from opug twitter about upcoming meeting", {"days": -1}),
    MeetupTask("tweet from linkedin about upcoming meeting", {"weeks": -2}),
    MeetupTask("tweet from linkedin about upcoming meeting", {"weeks": -1}),
    MeetupTask("tweet from linkedin about upcoming meeting", {"days": -1}),
    # after meetup
    MeetupTask("tweet from opug thanking presenters and sponsors", {"days": 0}),
    MeetupTask("push out meeting followup survey to attendees", {"days": 2}),
    MeetupTask("send out intro survey to new attendees", {"days": 2}),
]


def get_project_name(meetup_date: date) -> str:
    """
    returns a formtting project name following "{month}-opug-meetup" format
    """
    month = calendar.month_name[meetup_date.month].lower()  # typing: str
    return f"{month}-opug-meetup"


def add_opug_tasks(
    task_client: TaskWarrior,
    project_name: str,
    meetup_date: date,
    task_list: typing.List[MeetupTask],
    tags: typing.List[str] = DEFAULT_TAGS,
    priority: str = DEFAULT_PRIORITY,
):
    """
    adds the task list to taskwarrior.

    TODO: this could be refactored into a utils.py if I like it enough...
    """
    for task_meta in task_list:
        due_date = meetup_date + relativedelta(**task_meta.date_offset)
        print(f"creating {task_meta.description} due on {due_date}")
        task_client.task_add(
            description=task_meta.description,
            tags=tags,
            priority=priority,
            due=due_date,
            project=project_name,
        )


@click.command()
@click.argument("meetup_date", type=click.DateTime())
def create_opug_meetup_tasks(meetup_date: datetime):
    """
    CLI to create tasks for a given meetup date using the default task list.
    """
    # parse string to date
    # date_parser = parser()
    # meetup_dt = parser.parse(meetup_date)
    # print(f"converted {meetup_date} into {meetup_dt}")
    print(f"building tasks for meetup on {meetup_date}")
    logger.debug("Initializing TaskWarrior client")
    task_client = TaskWarrior(marshal=True)

    project_name = get_project_name(meetup_date=meetup_date)
    add_opug_tasks(
        task_client=task_client,
        project_name=project_name,
        meetup_date=meetup_date,
        task_list=TASK_LIST,
    )


if __name__ == "__main__":
    create_opug_meetup_tasks()
