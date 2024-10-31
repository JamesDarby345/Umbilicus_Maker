import matplotlib.pyplot as plt
import json
import argparse
from matplotlib.backend_bases import MouseButton
import vesuvius
import zarr

class PointCollector:
    def __init__(self, scroll_volume, step=500, sname='', zpos=2):
        self.volume = scroll_volume
        self.step = step
        self.points = []
        self.current_z = None
        self.sname = sname
        self.zpos = zpos

    def onclick(self, event):
        if event.button is MouseButton.LEFT and event.inaxes is not None:
            x, y = int(event.xdata), int(event.ydata)
            self.points.append([self.current_z, y, x])
            print(f"Point added at z={self.current_z}, y={y}, x={x}")
            plt.close()

    def collect_points(self):
        z_axis_length = self.volume.shape()[self.zpos]-1
        for z in range(0, z_axis_length + self.step, self.step):
            if z > z_axis_length:
                z = z_axis_length
            self.current_z = z
            fig, ax = plt.subplots(figsize=(12, 8))
            if self.zpos==0:
                ax.imshow(self.volume[z,:,:])
            elif self.zpos==1:
                ax.imshow(self.volume[:,z,:])
            else:
                ax.imshow(self.volume[:,:,z])
            ax.set_title(f'Slice {z}/{z_axis_length}. Double click to select point.')
            
            fig.canvas.mpl_connect('button_press_event', self.onclick)
            plt.show()
            
            if z == z_axis_length:
                break
            
        filename = f'{self.sname}_zyx_umbilicus_points.json' if self.sname else 'zyx_umbilicus_points.json'
        with open(filename, 'w') as f:
            json.dump(self.points, f, indent=2)
        print(f"Saved {len(self.points)} points to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Collect points from scroll volume')
    parser.add_argument('--sid', default='1', help='Scroll id [1,2,3,4]')
    parser.add_argument('--energy', type=int, default=54, help='energy value; kev')
    parser.add_argument('--res', type=float, default=7.91, help='Scan resolution value [7.91, 3.24]')
    parser.add_argument('--step', type=int, default=500, help='Step size between z slices to specify points')
    parser.add_argument('--local_zarr_path', default='', help='Local path to zarr file')
    parser.add_argument('--zpos', type=int, default=0, help='position of z axis in the data shape; 0=[z,:,:], 1=[:,z,:], 2=[:,:,z] the axis to make the umbilicus across')
    args = parser.parse_args()

    if args.local_zarr_path:
        # scroll = zarr.open(args.local_zarr_path)
        scroll = vesuvius.Volume(type="scroll", scroll_id=args.sid, energy=args.energy, resolution=args.res, domain='local', path=args.local_zarr_path)
    else:
        scroll = vesuvius.Volume(type="scroll", scroll_id=args.sid, energy=args.energy, resolution=args.res)

    scroll_name = 's'+args.sid+'_'+str(args.energy)+'kev_'+str(args.res)+'um'
    print("scroll name ", scroll_name)
    print("z position is ", args.zpos, " scroll shape is ", scroll.shape())
    collector = PointCollector(scroll, step=args.step, sname=scroll_name, zpos=args.zpos)
    collector.collect_points()

if __name__ == '__main__':
    main() 