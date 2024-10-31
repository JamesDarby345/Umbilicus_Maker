import matplotlib.pyplot as plt
import json
import argparse
from matplotlib.backend_bases import MouseButton
import vesuvius
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue
import threading
import time

class PointCollector:
    def __init__(self, scroll_volume, step=500, sname='', zpos=2, num_workers=2, 
                 sx=None, sy=None, ex=None, ey=None):
        self.volume = scroll_volume
        self.step = step
        self.points = []
        self.current_z = None
        self.sname = sname
        self.zpos = zpos
        self.slice_cache = {}
        self.sx = sx or 0
        self.sy = sy or 0
        self.ex = ex or (scroll_volume.shape()[2] if zpos != 2 else scroll_volume.shape()[1])
        self.ey = ey or (scroll_volume.shape()[1] if zpos != 1 else scroll_volume.shape()[0])
        self.precache_complete = False
        self.load_queue = PriorityQueue()
        self.executor = ThreadPoolExecutor(max_workers=num_workers)  # Configurable workers
        self.loading_lock = threading.Lock()
        self.current_future = None

    def onclick(self, event):
        if event.button is MouseButton.LEFT and event.inaxes is not None:
            x = int(event.xdata) + self.sx
            y = int(event.ydata) + self.sy
            self.points.append([self.current_z, y, x])
            print(f"Point added at z={self.current_z}, y={y}, x={x}")
            plt.close()

    def load_slice(self, z):
        start_time = time.time()
        print(f"[DEBUG] Requesting slice z={z}")
        
        with self.loading_lock:
            if z in self.slice_cache:
                print(f"[DEBUG] Slice z={z} found in cache, returning immediately")
                return self.slice_cache[z]
            
            print(f"[DEBUG] Starting to load slice z={z}")
            if self.zpos == 0:
                slice_data = self.volume[z, self.sy:self.ey, self.sx:self.ex]
            else:
                slice_data = self.volume[self.sx:self.ex, self.sy:self.ey, z]
            
            load_time = time.time() - start_time
            print(f"[DEBUG] Loaded slice z={z} in {load_time:.2f}s")
            
            self.slice_cache[z] = slice_data
            return slice_data

    def prefetch_worker(self):
        while True:
            priority, z = self.load_queue.get()
            if z == -1:
                print("[DEBUG] Prefetch worker received stop signal")
                break
            if z not in self.slice_cache:
                print(f"[DEBUG] Prefetch worker starting load for z={z} (priority={priority})")
                self.load_slice(z)
                print(f"[DEBUG] Prefetch worker completed load for z={z}")

    def collect_points(self):
        z_axis_length = self.volume.shape()[self.zpos]-1
        
        # Start prefetch worker
        self.executor.submit(self.prefetch_worker)
        
        # Queue up initial prefetch requests
        next_z = self.step
        while next_z <= z_axis_length:
            self.load_queue.put((1, next_z))  # Priority 1 for prefetch
            next_z += self.step

        # Main loop
        for z in range(0, z_axis_length + self.step, self.step):
            if z > z_axis_length:
                z = z_axis_length
            self.current_z = z
            
            # Priority load current slice
            slice_data = self.load_slice(z)
            
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.imshow(slice_data)
            ax.set_title(f'Slice {z}/{z_axis_length}. Double click to select point.')
            
            fig.canvas.mpl_connect('button_press_event', self.onclick)
            plt.show()
            
            if z == z_axis_length:
                break

        # Cleanup
        self.load_queue.put((0, -1))  # Stop the prefetch worker
        self.executor.shutdown()
        
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
    parser.add_argument('--zpos', type=int, default=0, help='the axis order of the volume; 0=[z,y,x], 1=[x,y,z]')
    parser.add_argument('--AB', default='', help='Scroll A or B scan if relevant for json naming,just append string val after s#')
    parser.add_argument('--workers', type=int, default=2, 
                      help='Number of background workers for prefetching slices')
    parser.add_argument('--sx', type=int, help='Start X coordinate')
    parser.add_argument('--sy', type=int, help='Start Y coordinate')
    parser.add_argument('--ex', type=int, help='End X coordinate')
    parser.add_argument('--ey', type=int, help='End Y coordinate')
    args = parser.parse_args()

    if args.local_zarr_path:
        # scroll = zarr.open(args.local_zarr_path)
        scroll = vesuvius.Volume(type="scroll", scroll_id=args.sid, energy=args.energy, resolution=args.res, domain='local', path=args.local_zarr_path)
    else:
        scroll = vesuvius.Volume(type="scroll", scroll_id=args.sid, energy=args.energy, resolution=args.res)
        print('loading from dataserver, may take a considerable amount of time to load the slices')

    scroll_name = 's'+args.sid+args.AB+'_'+str(args.energy)+'kev_'+str(args.res)+'um'
    print("scroll name ", scroll_name)
    print("z position is ", args.zpos, " scroll shape is ", scroll.shape())
    collector = PointCollector(scroll, step=args.step, sname=scroll_name, 
                             zpos=args.zpos, num_workers=args.workers,
                             sx=args.sx, sy=args.sy, ex=args.ex, ey=args.ey)
    collector.collect_points()

if __name__ == '__main__':
    main() 