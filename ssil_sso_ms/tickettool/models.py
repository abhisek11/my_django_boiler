from django.db import models
from dynamic_media import get_directory_path
import time
from validators import validate_file_extension
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

class SupportType(models.Model):
    type_name = models.CharField(max_length=50,null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='queue_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='queue_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='queue_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'queue'

def unique_rand_ticket():
    while True:
        code = "TPMS" + str(int(time.time()))
        if not Ticket.objects.filter(ticket_g_id=code).exists():
            return code


class Ticket(models.Model):
    """
    To allow a ticket to be entered as quickly as possible, only the
    bare minimum fields are required. These basically allow us to
    sort and manage the ticket. The user can always go back and
    enter more information later.
    A good example of this is when a customer is on the phone, and
    you want to give them a ticket ID as quickly as possible. You can
    enter some basic info, save the ticket, give the customer the ID
    and get off the phone, then add in further detail at a later time
    (once the customer is not on the line).
    Note that assigned_to is optional - unassigned tickets are displayed on
    the dashboard to prompt users to take ownership of them.
    
    editor :- abhishek.singh@shyamfuture.com
    """

    OPEN_STATUS = 1
    REOPENED_STATUS = 2
    RESOLVED_STATUS = 3
    CLOSED_STATUS = 4
    DUPLICATE_STATUS = 5
    PROCESSING_STATUS= 6

    STATUS_CHOICES = (
        (OPEN_STATUS, 'Open'),
        (REOPENED_STATUS,'Reopened'),
        (RESOLVED_STATUS, 'Resolved'),
        (CLOSED_STATUS,'Closed'),
        (DUPLICATE_STATUS,'Duplicate'),
        (PROCESSING_STATUS,'Processing')
    )

    PRIORITY_CHOICES = (
        (1, '1. Critical'),
        (2, '2. High'),
        (3, '3. Normal'),
        (4, '4. Low'),
        (5, '5. Very Low'),
    )
    ticket_g_id = models.CharField(max_length=50, unique=True,default=unique_rand_ticket)

    type_of_issue = models.ForeignKey(SupportType,on_delete=models.CASCADE,verbose_name='SupportType')

    created = models.DateTimeField('Created',blank=True,help_text='Date this ticket was first created')

    modified = models.DateTimeField('Modified',blank=True,help_text='Date this ticket was most recently changed.')

    submitter_email = models.EmailField('Submitter E-Mail',blank=True,null=True,
        help_text='The submitter will receive an email for all public '
                    'follow-ups left for this task.')

    assigned_to = models.ForeignKey(User,on_delete=models.CASCADE,related_name='assigned_to',
        blank=True,null=True,verbose_name='Assigned to')

    status = models.IntegerField('Status',choices=STATUS_CHOICES,default=OPEN_STATUS,)

    on_hold = models.BooleanField('On Hold',blank=True,default=False,
        help_text='If a ticket is on hold, it will not automatically be escalated.')

    description = models.TextField('Description',blank=True,null=True,
        help_text='The content of the customers query.')

    resolution = models.TextField('Resolution',blank=True,null=True,
        help_text='The resolution provided to the customer by our staff.')

    priority = models.IntegerField('Priority',choices=PRIORITY_CHOICES,default=3,blank=3,
        help_text='1 = Highest Priority, 5 = Low Priority')

    due_date = models.DateTimeField('Due on',blank=True,null=True,)
    image_name = models.CharField(max_length=50,blank=True,null=True)
    image = models.FileField(upload_to=get_directory_path,
                                         default=None,
                                         blank=True, null=True,
                                         validators=[validate_file_extension]
                                         )

    last_escalation = models.DateTimeField(blank=True,null=True,editable=False,
        help_text='The date this ticket was last escalated - updated '
                    'automatically by management/commands/escalate_tickets.py.')

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='ticket_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='ticket_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='ticket_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'ticket'
        
    def _get_assigned_to(self):
        """ Custom property to allow us to easily print 'Unassigned' if a
        ticket has no owner, or the users name if it's assigned. If the user
        has a full name configured, we use that, otherwise their username. """
        if not self.assigned_to:
            return _('Unassigned')
        else:
            if self.assigned_to.get_full_name():
                return self.assigned_to.get_full_name()
            else:
                return self.assigned_to.get_username()
    get_assigned_to = property(_get_assigned_to)

    def _get_ticket(self):
        """ A user-friendly ticket ID, which is a combination of ticket ID
        and queue slug. This is generally used in e-mail subjects. """

        return u"[%s]" % self.ticket_for_url
    ticket = property(_get_ticket)

    def _get_ticket_for_url(self):
        """ A URL-friendly ticket ID, used in links. """
        return u"%s-%s" % (self.queue.slug, self.id)
    ticket_for_url = property(_get_ticket_for_url)

    def _get_priority_css_class(self):
        """
        Return the boostrap class corresponding to the priority.
        """
        if self.priority == 2:
            return "warning"
        elif self.priority == 1:
            return "danger"
        elif self.priority == 5:
            return "success"
        else:
            return ""
    get_priority_css_class = property(_get_priority_css_class)

    def _get_status(self):
        """
        Displays the ticket status, with an "On Hold" message if needed.
        """
        held_msg = ''
        if self.on_hold:
            held_msg = _(' - On Hold')
        dep_msg = ''
        if not self.can_be_resolved:
            dep_msg = _(' - Open dependencies')
        return u'%s%s%s' % (self.get_status_display(), held_msg, dep_msg)
    get_status = property(_get_status)

    def _get_ticket_url(self):
        """
        Returns a publicly-viewable URL for this ticket, used when giving
        a URL to the submitter of a ticket.
        """
        from django.contrib.sites.models import Site
        from django.core.exceptions import ImproperlyConfigured
        from django.urls import reverse
        try:
            site = Site.objects.get_current()
        except ImproperlyConfigured:
            site = Site(domain='configure-django-sites.com')
        return u"http://%s%s?ticket=%s&email=%s" % (
            site.domain,
            reverse('helpdesk:public_view'),
            self.ticket_for_url,
            self.submitter_email
        )
    ticket_url = property(_get_ticket_url)

    def _get_staff_url(self):
        """
        Returns a staff-only URL for this ticket, used when giving a URL to
        a staff member (in emails etc)
        """
        from django.contrib.sites.models import Site
        from django.core.exceptions import ImproperlyConfigured
        from django.urls import reverse
        try:
            site = Site.objects.get_current()
        except ImproperlyConfigured:
            site = Site(domain='configure-django-sites.com')
        return u"http://%s%s" % (
            site.domain,
            reverse('helpdesk:view',
                    args=[self.id])
        )
    staff_url = property(_get_staff_url)

    def _can_be_resolved(self):
        """
        Returns a boolean.
        True = any dependencies are resolved
        False = There are non-resolved dependencies
        """
        OPEN_STATUSES = (Ticket.OPEN_STATUS, Ticket.REOPENED_STATUS)
        return TicketDependency.objects.filter(ticket=self).filter(
            depends_on__status__in=OPEN_STATUSES).count() == 0
    can_be_resolved = property(_can_be_resolved)

    class Meta:
        get_latest_by = "created"
        ordering = ('id',)
        verbose_name ='Ticket'
        verbose_name_plural ='Tickets'

    def __str__(self):
        return '%s %s' % (self.id, self.title)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('helpdesk:view', args=(self.id,))

    def save(self, *args, **kwargs):
        if not self.id:
            # This is a new ticket as no ID yet exists.
            self.created = timezone.now()

        if not self.priority:
            self.priority = 3

        self.modified = timezone.now()

        super(Ticket, self).save(*args, **kwargs)

    @staticmethod
    def queue_and_id_from_query(query):
        # Apply the opposite logic here compared to self._get_ticket_for_url
        # Ensure that queues with '-' in them will work
        parts = query.split('-')
        queue = '-'.join(parts[0:-1])
        return queue, parts[-1]