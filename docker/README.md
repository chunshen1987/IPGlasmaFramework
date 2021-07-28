## Using IPGlasmaFramework via Docker

Docker is a software tool that allows one to deploy an application in a portable environment. A docker "image" can be created for the application, allowing any user to run a docker "container" from this image.

### 1. Build a new Docker image
We can build a docker image for the IPGlasmaFramework package using the following command,

```
	docker build -t chunshen1987/ipglasmaframework:latest .
```

### 2. Run IPGlasmaFramework
The docker container has ready compiled all the software packages for IPGlasmaFramework.

```
    docker run -it --rm --name myIPGlasma chunshen1987/ipglasmaframework:latest
```

### 3. To delete all the Docker images in your laptop

```
    docker system prune -a
```

### 4. Push the Docker image to the Docker Hub

```
    docker push chunshen1987/ipglasmaframework:latest
```

## Using IPGlasmaFramework via Singularity

Use the following command to create a singularity image (sif) from the
docker image,

```
    singularity pull docker://chunshen1987/ipglasmaframework:latest
```

To run the singularity image, `singularity run ipglasmaframework_lastest.sif`
