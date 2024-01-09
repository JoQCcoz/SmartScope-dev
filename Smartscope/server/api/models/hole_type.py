


from .base_model import *

class HoleType(BaseModel):
    holetype_id = models.CharField(max_length=30, blank=True, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    hole_size = models.FloatField(null=True, blank=True, default=None)
    hole_spacing = models.FloatField(null=True, blank=True, default=None)

    @property
    def pitch(self):
        return self.hole_size + self.hole_spacing

    class Meta(BaseModel.Meta):
        db_table = 'holetype'

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.holetype_id = self.name.replace('/', '_').replace(' ', '_').lower()
        super().save(*args, **kwargs)