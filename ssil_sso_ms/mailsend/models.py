from django.db import models

class MailTemplate(models.Model):
    name=models.CharField(max_length=255)
    code=models.CharField(max_length=255)
    subject=models.CharField(max_length=255)
    html_content=models.TextField()
    template_variable=models.TextField()

    class Meta:
        db_table = 'mail_template'

    def __str__(self):
        return self.name
