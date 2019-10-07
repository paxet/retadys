from flask import current_app
from flask_mail import Mail, Message

__author__ = 'jcaballero'

mailer = Mail()


def replace_for_html(text):
    """
    Replaces characters with the code of their html versions
    :param text: The original string
    :return:
    """
    spanish_code = {'á': '&aacute;', 'é': '&eacute;', 'í': '&iacute;', 'ó': '&oacute;', 'ú': '&uacute;',
                    'ñ': '&ntilde;', '¿': '&iquest;'}
    return "".join(spanish_code.get(k, k) for k in text).replace('\n', '<br />')


def send_mail(subject, body, recipients, attachment=None, mimetype=None):
    """
    Send formatted html emails
    :param subject: The subject of the email
    :param body: The body of the email
    :param recipients: Recipients to send the email to
    :param attachment: Path of the attachment to send
    :param mimetype: Two-part identifier format for attachment. Example: application/zip
    :return:
    """
    msg = Message(subject=subject, recipients=recipients)
    msg.html = replace_for_html(body)
    if attachment and mimetype:
        with current_app.open_resource(attachment) as fp:
            msg.attach(attachment, mimetype, fp.read())
    mailer.send(msg)
