# oil-tank-detector

A GBDX task that detects oil tanks with max-tree filtering. The input to the task is a panchromatic image in UTM projection. The output is a geojson file with the detection bounding boxes.

The algorithm uses morphological operations to increase the compactness of oil tanks, and then performs max-tree filtering based on area and compactness, followed by vectorization of the raster output to produce the detected oil tank axis aligned bounding boxes.

Check out [circular-tank-detector](https://github.com/platformstories/circular-tank-detector) for a more accurate solution to the problem of oil tank detection.

**Comments**

+ Depending on the specified minimum compactness, compact features other than oil tanks might be detected. Keep in mind that detection is based on purely geometric properties.
+ If the input image size is > 3-4GB, then specify a smaller area bounding box.

## Run

In a Python terminal:

```python
import gbdxtools

gbdx = gbdxtools.Interface()

otd = gbdx.Task('oil-tank-detector')
otd.inputs.image = 's3://gbd-customer-data/32cbab7a-4307-40c8-bb31-e2de32f940c2/platform-stories/oil-tanks/image-houston-pan'
otd.inputs.bbox = '-95.14483630657196,29.696617936567343,-94.98828113079071,29.773830057098092'

# Run workflow and save results
wf = gbdx.Workflow([otd])
wf.savedata(otd.outputs.detections, 'platform-stories/trial-runs/oil-tanks')
wf.execute()
```

## Input ports

| Name  | Type |  Description | Required |
|-------|--------------|----------------|----------------|
| image | Directory | Contains input panchromatic image in UTM projection. If more than one images are contained in this directory, one is picked arbitrarily. | True |
| bbox | String | Bounding box coordinates in lat/long. The format is 'W,S,E,N'. Default is None (entire input image). | False |
| min_compactness | string | Minimum compactness. Default is 0.95. | False |
| min_size | string | Minimum area in m2. Default is 100. | False |
| max_size | string | Maximum area in m2. Default is 12000. | False |


## Output ports

| Name  | Type | Description                                    |
|-------|---------|---------------------------------------------------|
| detections | directory | Contains geojson file with detection bounding boxes. |

## Development

### Build the Docker image

You need to install [Docker](https://docs.docker.com/engine/installation/).

Clone the repository:

```bash
git clone https://github.com/platformstories/oil-tank-detector
```

Then:

```bash
cd oil-tank-detector
docker build --build-arg PROTOUSER=<GitHub username> \
             --build-arg PROTOPASSWORD=<GitHub password> \
             -t oil-tank-detector .
```

### Try out locally

Create a container in interactive mode and mount the sample input under `/mnt/work/input/`:

```bash
docker run -v full/path/to/sample-input:/mnt/work/input -it oil-tank-detector
```

Then, within the container:

```bash
python /oil-tank-detector.py
```

Confirm that the output geojson is under `/mnt/work/output/detections`.

### Docker Hub

Login to Docker Hub:

```bash
docker login
```

Tag your image using your username and push it to DockerHub:

```bash
docker tag oil-tank-detector yourusername/oil-tank-detector
docker push yourusername/oil-tank-detector
```

The image name should be the same as the image name under containerDescriptors in oil-tank-detector.json.

Alternatively, you can link this repository to a [Docker automated build](https://docs.docker.com/docker-hub/builds/).
Every time you push a change to the repository, the Docker image gets automatically updated.

### Register on GBDX

In a Python terminal:

```python
import gbdxtools
gbdx = gbdxtools.Interface()
gbdx.task_registry.register(json_filename='oil-tank-detector.json')
```

Note: If you change the task image, you need to reregister the task with a higher version number
in order for the new image to take effect. Keep this in mind especially if you use Docker automated build.
