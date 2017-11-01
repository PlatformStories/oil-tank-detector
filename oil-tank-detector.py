import json
import os
import protogen
import shutil

input_ports_location = '/mnt/work/input/'
output_ports_location = '/mnt/work/output/'

# Get image directory
image_dir = os.path.join(input_ports_location, 'image')

# Point to image file. If there are multiple tif's in multiple subdirectories, pick one.
image_path, image = [(dp, f) for dp, dn, fn in os.walk(image_dir) for f in fn if ('tif' in f) or ('TIF' in f)][0]

# Read from ports.json
input_ports_path = os.path.join(input_ports_location, 'ports.json')
if os.path.exists(input_ports_path):
    string_ports = json.load(open(input_ports_path))
else:
    string_ports = None

if string_ports:

    bbox = string_ports.get('bbox', '')
    if bbox: bbox = map(float, bbox.split(','))
    min_compactness = float(string_ports.get('min_compactness', '0.95'))
    min_size = int(string_ports.get('min_size', '100'))
    max_size = int(string_ports.get('max_size', '12000'))

else:

    bbox = ''
    min_compactness = 0.95
    min_size = 100
    max_size = 12000

# Create output directory
output_dir = os.path.join(output_ports_location, 'detections')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Make input image directory the working directory
os.chdir(image_path)

# Run algo
print 'Oil tank extraction'

e = protogen.Interface('extract', 'objects')
e.extract.objects.type = 'tanks'
e.extract.objects.shade = 'bright'
e.extract.objects.visualization = 'binary'
e.extract.objects.multiplier = 2.0
e.extract.objects.dark_hole_size = 20
e.extract.objects.dark_line_radius = 2.0
e.extract.objects.bright_line_radius = 1.0
e.extract.objects.bright_patch_size = 20
e.athos.tree_type = 'max_tree'
e.athos.area.usage = ['remove if outside']
e.athos.area.min = [min_size]
e.athos.area.max = [max_size]
e.athos.compactness.usage = ['remove if less']
e.athos.compactness.min = [min_compactness]
e.athos.compactness.export = [1]
e.image = image
if bbox:
    W, S, E, N = bbox
    e.image_config.input_latlong_rectangle = [W, N, E, S]
e.execute()

print 'Vectorization'
v = protogen.Interface('vectorizer', 'bounding_box')
v.vectorizer.bounding_box.filetype = 'geojson'
v.athos.tree_type = 'union-find'
v.athos.dimensions = 2
v.athos.area.export = [1]
v.image = e.output
v.image_config.bands = [1]
v.execute()

# Rename geojson and copy it to output folder
shutil.move(v.output, 'detections.geojson')
shutil.copy('detections.geojson', output_dir)
