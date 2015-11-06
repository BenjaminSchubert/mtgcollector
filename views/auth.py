import flask
from flask_login import login_user, login_required, logout_user, current_user
from mtgcollector import app
from views.forms.auth import LoginForm


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated():
        return flask.redirect(flask.url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        login_user(form.user)

        return flask.redirect(flask.request.values.get("next") or flask.request.referrer or "index")

    return flask.render_template(
        'form.html', form=form, title="Login", action_url=flask.url_for("login", next=flask.request.referrer)
    )


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.request.referrer or "index")
