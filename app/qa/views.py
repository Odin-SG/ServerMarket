from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app import db
from app.models.server import Server
from app.models.server_question import ServerQuestion
from app.models.server_answer import ServerAnswer
from app.models.user import UserRole
from app.qa.forms import QuestionForm, AnswerForm
from app.user.views import get_server_stats

bp = Blueprint('qa', __name__, url_prefix='/servers')


@bp.route('/<slug>/qa', methods=['GET', 'POST'])
def server_qa(slug):
    server = Server.query.filter_by(slug=slug).first_or_404()

    stats = get_server_stats(server.id)

    q_form = QuestionForm()
    a_form = AnswerForm()

    if q_form.validate_on_submit() and 'question_id' not in request.form:
        if not current_user.is_authenticated:
            flash('Чтобы задать вопрос, войдите в систему.', 'warning')
            return redirect(url_for('auth.login'))
        q = ServerQuestion(server_id=server.id, user_id=current_user.id, text=q_form.text.data)
        db.session.add(q)
        db.session.commit()
        flash('Вопрос добавлен', 'success')
        return redirect(url_for('qa.server_qa', slug=slug) + f'#q{q.id}')

    if request.method == 'POST' and request.form.get('question_id'):
        if not (current_user.is_authenticated and current_user.role in (UserRole.MODERATOR, UserRole.ADMIN)):
            flash('Ответы могут оставлять только модераторы и админы.', 'danger')
        else:
            if a_form.validate():
                qid = int(request.form['question_id'])
                ans = ServerAnswer(question_id=qid, user_id=current_user.id, text=a_form.text.data)
                db.session.add(ans)
                db.session.commit()
                flash('Ответ добавлен', 'success')
            else:
                for err in a_form.text.errors:
                    flash(err, 'danger')
        return redirect(url_for('qa.server_qa', slug=slug))

    questions = (ServerQuestion.query
                 .filter_by(server_id=server.id)
                 .order_by(ServerQuestion.created_at.desc())
                 .all())

    return render_template(
        'user/server_qa.html',
        server=server,
        stats=stats,
        questions=questions,
        q_form=q_form,
        a_form=a_form
    )