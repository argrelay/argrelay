
Go to the directory for docker image creation:

```
cd ./src/argrelay_docker_image_demo
```

To build an image, run:

```sh
docker build -t argrelay/demo .
```

To run the newly built image, run:

```sh
docker run -it argrelay/demo
```

<!--
    TODO: Automatically tag by the verion from git
-->

To tag the image:

```sh
docker image tag argrelay/demo argrelay/demo:v0.8.0.final
```

To push the images image, run:

```sh
docker push argrelay/demo:v0.8.0.final
docker push argrelay/demo
```

To play with creating of image manually starting from the base one, run:

```sh
docker run --name=argrelay -ti fedora
```

