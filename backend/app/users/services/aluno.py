from app.core.config import settings
from app.schemas.perfis import AlunoCreate
from app.utils import generate_password_reset_token, render_email_template, send_email


def email_cadastro_aluno(aluno: AlunoCreate):
    token = generate_password_reset_token(aluno.email)
    html_content = render_email_template(
        template_name='convite_email.html',
        context={"nome_completo": aluno.nome, 'token': token, 'host': settings.PROJETO_DSN},
    )
    send_email(
        email_to=aluno.email,
        subject='Convite Abrasileirar',
        html_content=html_content,
    )
    return True
