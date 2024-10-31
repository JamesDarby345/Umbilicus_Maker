## Purpose of this repo
This repo provides .json files that specify umbilicus points for each of the 6 major released scroll scans as of october 2024.<br>
The .json files were created by clicking on the approximate umbilicus point every 500 voxels along the z-axis as well as the last z-axis slice.
They are in *zyx* point format, and the scan is specified in the file name. 
The provided code is what was used to create the umbilicus files. It uses the [vesuvius package](https://github.com/ScrollPrize/vesuvius)
to remotely load the scans while also providing the option to specify a local zarr path which will allows the slices to load much faster.


To identify the scroll scan resolution and energy, this spreadsheet of the scans released 
up to march 2024 (no new major ones released as of october 2024) will help to specify the correct scan info: [Vesuvius Data Spreadsheet](https://docs.google.com/spreadsheets/d/1k-7HUyPSsE_Or-In-OrkbsXCLfPm1NTHj6vGvmH80R4/edit?usp=sharing)