from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    IntegerField,
    DateTimeLocalField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from portal.models.assignment import Assignment


class AssignmentForm(FlaskForm):
    """Form for creating or editing assignments by instructors/admins."""

    title = StringField(
        "Assignment Title",
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={"placeholder": "e.g., Create AWS VPC Architecture"},
    )
    description = TextAreaField(
        "Description & Requirements",
        validators=[DataRequired(), Length(min=10)],
        render_kw={
            "rows": 6,
            "placeholder": "Detail requirements, deliverables, grading rubrics, and submission guidelines...",
        },
    )
    assignment_type = SelectField(
        "Assignment Type",
        choices=[
            (Assignment.TYPE_GROUP, "Group Assignment"),
            (Assignment.TYPE_INDIVIDUAL, "Individual Assignment"),
        ],
        default=Assignment.TYPE_GROUP,
    )
    max_group_size = SelectField(
        "Group Size (Members per Team)",
        choices=[
            ("1", "1 Member (Individual)"),
            ("2", "2 Members"),
            ("3", "3 Members (Standard)"),
            ("4", "4 Members"),
            ("5", "5 Members"),
        ],
        default="3",
        coerce=int,
    )
    max_groups = IntegerField(
        "Maximum Allowed Teams",
        validators=[DataRequired(), NumberRange(min=1, max=50)],
        default=1,
        render_kw={"help_text": "Number of official teams eligible for this assignment (e.g., 1 for single cohort group)."},
    )
    due_date = DateTimeLocalField(
        "Submission Deadline",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        render_kw={"placeholder": "YYYY-MM-DDTHH:MM"},
    )
    status = SelectField(
        "Assignment Status",
        choices=[
            (Assignment.STATUS_OPEN, "OPEN - Accepting Team Members"),
            (Assignment.STATUS_FULL, "FULL - Group Capacity Reached"),
            (Assignment.STATUS_CLOSED, "CLOSED - No Longer Accepting"),
        ],
        default=Assignment.STATUS_OPEN,
    )
    submit = SubmitField("Save Assignment")

    def validate_max_group_size(self, field):
        if self.assignment_type.data == Assignment.TYPE_INDIVIDUAL and field.data != 1:
            raise ValidationError("Individual assignments must have group size of 1.")
        if self.assignment_type.data == Assignment.TYPE_GROUP and field.data < 2:
            raise ValidationError("Group assignments must have a group size between 2 and 5.")


class AssignmentFilterForm(FlaskForm):
    """Filter and search form for assignments list."""

    search = StringField("Search", render_kw={"placeholder": "Search by title or description..."})
    status = SelectField(
        "Status",
        choices=[
            ("", "All Statuses"),
            (Assignment.STATUS_OPEN, "Open"),
            (Assignment.STATUS_FULL, "Full"),
            (Assignment.STATUS_CLOSED, "Closed"),
        ],
        default="",
    )
    assignment_type = SelectField(
        "Type",
        choices=[
            ("", "All Types"),
            (Assignment.TYPE_GROUP, "Group"),
            (Assignment.TYPE_INDIVIDUAL, "Individual"),
        ],
        default="",
    )
    sort_by = SelectField(
        "Sort By",
        choices=[
            ("newest", "Newest First"),
            ("oldest", "Oldest First"),
            ("title_asc", "Title (A-Z)"),
            ("title_desc", "Title (Z-A)"),
            ("due_date", "Due Date (Soonest)"),
        ],
        default="newest",
    )
