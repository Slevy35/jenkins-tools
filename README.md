# jenkins-tools
Jenkins utils to help you to manage your jenkins cluster

## Build
Use docker to build the package
```
make build
```

## Run
The utils can be executed in docker and locally.

```
## Locally
JENKINS_USERNAME=<JENKINS_USERNAME> -e JENKINS_PASSWORD=<JENKINS_PASSWORD> tools/<TOOL_NAME> -h

## Docker
docker run -it -e JENKINS_USERNAME=<JENKINS_USERNAME> -e JENKINS_PASSWORD=<JENKINS_PASSWORD> docker-tools:latest <TOOL_NAME> -h
```