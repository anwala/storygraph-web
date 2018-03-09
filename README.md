# [storygraph-web](http://storygraph.cs.odu.edu/)

Git repo for storygraph web viewer

## To build images
```
$ docker build -t storygraph-web:latest .
```

## To run server container
```
$ docker run -d -p [Port]:5000 [/host/path/to/data/]:/data storygraph-web
```
Sample content of ```[/host/path/to/data/]``` can be found [here](https://github.com/anwala/storygraph-data)