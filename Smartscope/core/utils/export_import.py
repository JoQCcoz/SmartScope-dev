from Smartscope.core.models import AutoloaderGrid
from Smartscope.server.api.serializers.export_serializers import ExportMetaSerializer
from rest_framework_yaml.renderers import YAMLRenderer
import yaml

def export_grid(instance, export_to:str):
    serializer = ExportMetaSerializer(instance=instance)
    with open(export_to,'wb') as file:
        file.write(YAMLRenderer().render(data=serializer.data))

def import_grid(file_to_import:str):
    with open(file_to_import,'r') as file:
        data = yaml.safe_load(file) 
    grid= ExportMetaSerializer(data=data)
    grid.is_valid()
    print(grid.errors) 
    grid.save()