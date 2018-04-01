from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, Email, Length, ip_address
from flask_wtf import FlaskForm


class SwitchForm(FlaskForm):
    source_switch_ip = StringField('source_switch_ip', validators=[DataRequired(message="Source switch IP address must be populated."),
                                                                   ip_address(message="Source switch IP format should be: A.B.C.D")])
    destination_switch_ip = StringField('destination_switch_ip', validators=[DataRequired(message="Destination switch IP address must be populated."),
                                                                             ip_address(message="Destination switch IP format should be: A.B.C.D")])
    starting_clients = IntegerField('starting_clients')


class SparkForm(FlaskForm):
    spark_token = StringField('sparktoken', validators=[DataRequired(), Length(min=64, max=64, message="Spark tokens are 64 characters in length.")])
    team_name = StringField('teamname', validators=[DataRequired(message="A team name is required.")])
    space_name = StringField('spacename', validators=[DataRequired(message="A space name is required.")])
    user_email = StringField('email', validators=[Email(), DataRequired()])


class MigrateForm(FlaskForm):
    # There aren't any data fields on this form - stub
    pass
