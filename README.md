# KATALON INSIGHTS

https://insight-staging.katalon.com/

**Description**: Setup Katalon Insights Django server

------------------------------

## CONFIGURE

### Cloud Environment Config
**Mount folder : Application File**
Host  :  /workspace/
Container Path :  /workspace/

**Mount Folder: File System From EFS**
Host : /hdf5files/
Container Path :  /workspace/hdf5files

EFS File System Name : Katalon-Insight

/deloy/.ebextension/storage-efs-mountfilesystem.config :  this file will host to Host Server to folder "/hdf5files "

Description :  When performing to run deploy Docker Cluster , base on file  _Dockerrun.aws.json to execute mount folder from host to docker.  It will be mounted from /hd5files to container path /workspace/hdf5files/

### Environment

Windows 10, 64 bit
Python 3.6

### Install dependencies

```sh
$ pip install -r requirements.txt
```

### Run server

```sh
$ python manage.py runserver 0:8000
```

## FEATURES
1. Clustering
2. Graph stacktrace (katalon-graph)
3. Support big matrix calculation (katalon-graph)
4. Image Comparison (not merged)
5. Server performance analysis (pending)
6. Test cases correlation analysis (pending)


### Clustering
1. Cluster Project ID
```sh
https://insight-staging.katalon.com/insights/cluster/project_id

{
  "projectId": 29539,
  "SYSTEM_KEY": <SYSTEM_KEY>
}
```
2. Cluster within intervals
```sh
https://insight-staging.katalon.com/insights/cluster/within_interval

{
  "projectId": 29539,
  "startTime": "2010-01-10 00:00:00",
  "endTime": "2020-12-10 00:00:00",
  "SYSTEM_KEY": <SYSTEM_KEY>
}
```
3. Cluster execution
```sh
https://insight-staging.katalon.com/insights/cluster/execution_id

{
  "projectId": 29539,
  "executionId": 1753050,
  "SYSTEM_KEY": <SYSTEM_KEY>
}
```
