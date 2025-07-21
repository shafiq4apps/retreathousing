from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DecimalField, IntegerField, DateField, FileField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])

class TenantRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])

class PropertyForm(FlaskForm):
    address = TextAreaField('Address', validators=[DataRequired()], widget=TextArea())
    property_type = SelectField('Property Type', 
                               choices=[('apartment', 'Apartment'), ('house', 'House'), ('commercial', 'Commercial')],
                               validators=[DataRequired()])
    bedrooms = IntegerField('Bedrooms', validators=[Optional(), NumberRange(min=0)])
    bathrooms = IntegerField('Bathrooms', validators=[Optional(), NumberRange(min=0)])
    square_footage = IntegerField('Square Footage', validators=[Optional(), NumberRange(min=1)])
    rent_amount = DecimalField('Monthly Rent', validators=[Optional(), NumberRange(min=0)], places=2)
    description = TextAreaField('Description', validators=[Optional()])

class LeaseForm(FlaskForm):
    tenant_id = SelectField('Tenant', coerce=int, validators=[DataRequired()])
    property_id = SelectField('Property', coerce=int, validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    monthly_rent = DecimalField('Monthly Rent', validators=[DataRequired(), NumberRange(min=0)], places=2)
    security_deposit = DecimalField('Security Deposit', validators=[Optional(), NumberRange(min=0)], places=2)

class MessageForm(FlaskForm):
    recipient_id = SelectField('Recipient', coerce=int, validators=[DataRequired()])
    property_id = SelectField('Property (Optional)', coerce=int, validators=[Optional()])
    message_text = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=1000)])

class MaintenanceRequestForm(FlaskForm):
    property_id = SelectField('Property', coerce=int, validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[DataRequired()])
    priority = SelectField('Priority', 
                          choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
                          validators=[DataRequired()])

class DocumentUploadForm(FlaskForm):
    lease_id = SelectField('Lease', coerce=int, validators=[DataRequired()])
    document_type = SelectField('Document Type', 
                               choices=[('lease_agreement', 'Lease Agreement'), ('addendum', 'Addendum'), ('notice', 'Notice')],
                               validators=[DataRequired()])
    file = FileField('Document File', validators=[DataRequired()])