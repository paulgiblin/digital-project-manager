from flask import render_template, redirect, url_for, flash
from dpmapp.forms import SwitchForm, SparkForm, MigrateForm
from dpmapp.switchops import initialize_switches
from dpmapp.sparkops import initialize_spark
from dpmapp.migrateops import start_migration
from dpmapp.dpmapp import flash_errors
from . import app


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/switch/", methods=["GET", "POST"])
def switch():
    form = SwitchForm()
    if form.validate_on_submit():
        initialize_switches(form.source_switch_ip.data, form.destination_switch_ip.data, form.starting_clients.data)
        flash('Switch data saved')
        return redirect(url_for('switch'))
    flash_errors(form)
    return render_template('switch.html', form=form)


@app.route("/spark/", methods=["GET", "POST"])
def spark():
    form = SparkForm()
    if form.validate_on_submit():
        initialize_spark(form.spark_token.data, form.team_name.data, form.space_name.data, form.user_email.data)
        flash('Spark successfully initialized!')
        return redirect(url_for('spark'))
    flash_errors(form)
    return render_template('spark.html', form=form)


@app.route("/migrate/", methods=["GET", "POST"])
def migrate():
    form = MigrateForm()
    if form.validate_on_submit():
        flash('Migration initialized!')
        start_migration()
        return redirect(url_for('migrate'))

    return render_template('migrate.html', form=form)
