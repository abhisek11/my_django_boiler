from datetime import datetime

from attendance.models import AttendenceAction

def log(user,action,fields,before_content,after_content,section):
    action = AttendenceAction(
        user=user,
        # role=role,
        time_of_action=datetime.now(),
        action=action,
        fields=fields,
        before_content=before_content,
        after_content=after_content,
        section=section,
        
    )
    action.save()
