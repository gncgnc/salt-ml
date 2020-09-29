# SALT Machine Learning Repository

`jsonify.py` preprocesses the images in the format below:
```json

{
    "data": {
        <name/id of image> : {
            "path": <path to image>,
            "uri_suffix": <link id for SALT website>,
            "features": <place for feature vector of the image, empty arrays for now>
        }
    }
}
```

`extract_features.py` gets the feature vectors for the images using VGG16 trained on ImageNet images. 
It outputs data as below. 

```json
{
    <name/id of image>: {
        "path": <path to image>,
        "features": <place for feature vector of the image>
    }
}
```
Thanks to Gene Kogan from ml4a for the reference implementation [here](https://github.com/ml4a/ml4a-ofx/blob/master/scripts/tSNE-images.py).

## TODO

[ ] Merge outputs of both scripts
[ ] Compute closest neighbors