from flask import flash

# Process a list of errors and dump them into the Flask flash list
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error)
