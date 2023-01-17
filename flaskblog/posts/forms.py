from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    """ A class for that creates the update page form """
    title = StringField('Title', validators=[DataRequired()])
    content =  TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')