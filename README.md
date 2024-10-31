## Purpose of this repo
This repo provides .json files that specify umbilicus points for each of the major released scroll scans as of october 2024 in the umbilicus_points folder.<br>
The .json files were created by clicking on the approximate umbilicus point every 500 voxels along the z-axis as well as the last z-axis slice.
They are in *zyx* point format, and the scan is specified in the file name. 
For most users, the completed .json files are all that is needed.
There are also .obj files created from the .json files in the umbilicus_obj folder, which can be used to visualize the umbilicus points in a 3d viewer. They are esssentially a line. These are also z,y,x format.<br>
<img width="400" alt="Screenshot 2024-10-31 at 4 58 34 PM" src="https://github.com/user-attachments/assets/6c7d1f78-2f34-4840-aae7-8b0cec6d029d"><br>
Visualisation of umbillicus point .obj for scroll 1 as a line.

## Why umbilicus points are useful

The umbilicus points are used extensively in thaumato for winding angles and other calculations, but I could'nt find the code to create them after poking around in that large repo for a bit. Also only the s1 and s3 umbilicus points were provided with somewhat sparse sampling, without the point axis ordering specified. So I thought I would just do all the scans I have locally downloaded and document it a bit more clearly.

I wanted umbilicus points to help more robustly identify recto/verso sides of volumetric surface/sheet predictions. Like the predictions from bruniss' fibre/surface prediction models, especially in aggressively curved regions where more simple normal techniques fail or where multiple labels touch and overlap. 

Anouther motivator was, in the case where multiple labels touch and overlap in bruniss' prediction volumes, the umbilicus points can be used to identify the location of the center of the scroll, and then since the resulting labels are of approximately uniform thickness, they could then be seperated by assuming the first x voxels on the line from the center (from the umbilicus points) to the label instance are the first fibre/sheet, and the second x voxels on the line from the center to the label instance are the second fibre/sheet behind it that are touching. This could address the issue of the multiple labels touching and overlapping which is a common problem volumetric prediction methods.

## The code

The provided code is what was used to create the umbilicus files. It is provided so that if new scans are released, the umbilicus points can be created using the same method, though the scans would have to be either downloaded locally or available vis the vesuvius package. It uses the [vesuvius package](https://github.com/ScrollPrize/vesuvius)
to remotely load the scans while also providing the option to specify a local zarr path which will allows the slices to load much faster.
It is highly recommended to use the local zarr path option, as loading a 2d slice from the zarr, requires loading all the chunks that cross the z-axis slice, and this can take a very long time depending on download speed etc. (It would be better to load the .tif slices but that is not supported by the vesuvius library so would require more dev effort, and I already have the .json results so I didnt bother).

To identify the scroll scan resolution and energy, this spreadsheet of the scans released 
up to march 2024 (no new major ones released as of october 2024) will help to specify the correct scan info: [Vesuvius Data Spreadsheet](https://docs.google.com/spreadsheets/d/1k-7HUyPSsE_Or-In-OrkbsXCLfPm1NTHj6vGvmH80R4/edit?usp=sharing)

## Usage

### Environment

#### Conda
```
conda env create -f environment.yml
conda activate umbilicus_maker
```

#### Pip
```
pip install -r requirements.txt
```

### Basic Usage (umbilicus_maker.py)
This script allows you to manually click points along the umbilicus line of a scroll. For each z-slice, a matplotlib window will open where you can click to mark the umbilicus point.

```bash
python umbilicus_maker.py --sid 1 --energy 54 --res 7.91 --local_zarr_path /path/to/zarr
```

### Cached Version (umbilicus_maker_cache.py)
This version includes slice prefetching and caching for faster operation:

```bash
python umbilicus_maker_cache.py --sid 1 --energy 54 --res 7.91 --local_zarr_path /path/to/zarr --workers 2
```

### Key Parameters
- `--sid`: Scroll ID (1,2,3,4)
- `--energy`: Energy value in keV
- `--res`: Scan resolution in microns (7.91 or 3.24)
- `--step`: Z-axis step size between points (default: 500)
- `--local_zarr_path`: Path to local zarr files (recommended)
- `--zpos`: Position of z-axis in data shape (0=[z,y,x], 1=[x,y,z])
- `--AB`: Append 'A' or 'B' to scroll name if relevant
- `--workers`: (cache version only) Number of background workers for prefetching
- `--sx/sy/ex/ey`: (cache version only) Crop coordinates for focusing on specific regions

### Output
The scripts generate a JSON file named `s{id}{AB}_{energy}kev_{res}um_zyx_umbilicus_points.json` containing the clicked points in [z,y,x] format.

### Obj conversion
The points_to_obj.py script can be used to convert the .json files to .obj files in the umbilicus_obj folder.
```bash
python points_to_obj.py
```

### Maintenance
This is built on top of the vesuvius package, so if they release a new version, this code will need to be updated to work with the new version.

### Tips
- Using local zarr files is strongly recommended as remote loading can be very slow
- The cached version is preferred for large scans as it preloads upcoming slices
- Use the cropping parameters (sx,sy,ex,ey) to load less of the slice if the umbilicus point can be guranteed to be in a smaller center region.
