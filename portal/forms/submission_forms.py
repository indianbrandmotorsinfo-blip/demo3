from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, URL, Length, Optional
from portal.models.submission import Submission


class SubmissionForm(FlaskForm):
    """Student submission form."""

    repo_url = StringField(
        "GitHub Repository URL",
        validators=[
            DataRequired(message="GitHub repository URL is required."),
            URL(message="Please enter a valid URL (e.g., https://github.com/username/project)."),
        ],
        render_kw={"placeholder": "https://github.com/org/aws-vpc-project"},
    )
    docs_url = StringField(
        "Documentation URL",
        validators=[
            DataRequired(message="Documentation URL is required."),
            URL(message="Please enter a valid documentation link (e.g., Notion, Google Docs, or GitHub Pages)."),
        ],
        render_kw={"placeholder": "https://docs.aws.amazon.com or https://notion.so/project-spec"},
    )
    remarks = TextAreaField(
        "Remarks & Implementation Notes",
        validators=[Optional(), Length(max=2000)],
        render_kw={
            "rows": 4,
            "placeholder": "Provide notes regarding architecture decisions, test coverage, caveats, and credentials if needed...",
        },
    )
    submit = SubmitField("Submit Assignment for Review")


class ReviewSubmissionForm(FlaskForm):
    """Admin submission evaluation form."""

    status = SelectField(
        "Review Decision",
        choices=[
            (Submission.STATUS_APPROVED, "Approve Submission"),
            (Submission.STATUS_REJECTED, "Reject Submission (Request Revisions)"),
        ],
        validators=[DataRequired()],
    )
    feedback = TextAreaField(
        "Evaluator Feedback & Grade Notes",
        validators=[Optional(), Length(max=2000)],
        render_kw={
            "rows": 4,
            "placeholder": "Provide qualitative feedback, suggestions, or reasons for rejection...",
        },
    )
    submit = SubmitField("Record Review Decision")
