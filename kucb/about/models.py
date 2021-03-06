from django.db import models
from tinymce import models as tinymce_models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Content(models.Model):
    title = models.CharField(max_length=500)
    text = tinymce_models.HTMLField()
    image = models.FileField(upload_to="img", blank=True)
    slug = models.SlugField(blank=True, null=True)
    def __unicode__(self):
        return self.title
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Content, self).save(*args, **kwargs)

class JobCategory(models.Model):
    name = models.CharField(max_length=100)
    priority = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return self.name

class Bio(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="bio")
    name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    job_title = models.CharField(max_length=100)
    job_category = models.ForeignKey(JobCategory, blank=True, null=True, on_delete=models.SET_NULL, related_name="bios")
    image = models.FileField(upload_to="img", blank=True)
    text = tinymce_models.HTMLField()
    slug = models.SlugField(blank=True, null=True)
    visible = models.BooleanField(default=True)

    @models.permalink
    def get_absolute_url(self):
        return ('kucb.about.views.profile',[], {'slug':self.slug})

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Bio, self).save(*args, **kwargs)

@receiver(pre_delete, sender=Bio, dispatch_uid='handle_bio_delete')
def bio_delete_handler(sender, instance, using, **kwargs):
    for article in instance.articles.all():
        if not article.author_name:
            article.author_name = instance.name
            article.save()

class Announcement(models.Model):
    title = models.CharField(max_length = 500)
    text = tinymce_models.HTMLField()
    pub_date = models.DateTimeField('Date Published (optional)', blank=True, null=True)
    image = models.FileField(upload_to="img", blank=True)
    active = models.BooleanField()
    def __unicode__(self):
        return self.title

class Program(models.Model):
    title = models.CharField(max_length=500, unique=True)
    slug = models.SlugField(null=True, blank=True, editable=False)
    producer = models.ForeignKey(Bio, blank=True, null=True, on_delete=models.SET_NULL)
    producer_name = models.CharField(help_text='Optional, if not a KUCB person', blank=True, max_length=100)
    description = tinymce_models.HTMLField()
    link = models.CharField(max_length=200, blank=True)
    class Meta:
        ordering = ['title']
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Program, self).save(*args, **kwargs)
    @models.permalink
    def get_absolute_url(self):
        return ('kucb.about.views.program',[], {'slug':self.slug})
    def __unicode__(self):
        return self.title

class Schedule(models.Model):
    DAY_CHOICES=(
        ('Recurring',(
                (-3, 'Daily'),
                (-2, 'Weekdays'),
                (-1, 'Weekends'),
            )
        ),
        ('Single day',(
                (0, 'Monday'),
                (1, 'Tuesday'),
                (2, 'Wednesday'),
                (3, 'Thursday'),
                (4, 'Friday'),
                (5, 'Saturday'),
                (6, 'Sunday'),
            )
        ),
    )
    program = models.ForeignKey(Program, related_name="schedule")
    day = models.IntegerField(max_length=2, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

class TVSchedule(models.Model):
    DAY_CHOICES=(
        ('Recurring',(
                (-3, 'Daily'),
                (-2, 'Weekdays'),
                (-1, 'Weekends'),
            )
        ),
        ('Single day',(
                (0, 'Monday'),
                (1, 'Tuesday'),
                (2, 'Wednesday'),
                (3, 'Thursday'),
                (4, 'Friday'),
                (5, 'Saturday'),
                (6, 'Sunday'),
            )
        ),
    )
    program = models.ForeignKey(Program, related_name="tv-schedule")
    day = models.IntegerField(max_length=2, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
