# [storygraph-web](http://storygraph.cs.odu.edu/)

Git repo for storygraph web viewer

## To build images
```
$ docker build -t storygraph-web:latest .
```

## To run server container
```
$ docker run -d -p [Port]:5000 [/Path/To/StoryGraphData/]:/data storygraph-web
```

Where 
[Port]: 11111
[/Path/To/StoryGraphData/]: /data/anwala/IMLS/StoryGraph