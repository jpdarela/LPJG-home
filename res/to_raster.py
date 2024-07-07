from sys import argv
import os

from geo import get_bbox, pan_amazon
from reader import make_reader
from writer import sio_to_cf

ymin, ymax, xmin, xmax = get_bbox(pan_amazon)

# functionality to convert smartio to CF netcdf4 files
# Set an output folder
nc_out = "./cf_outputs"
os.makedirs(nc_out, exist_ok=True)


if __name__ == "__main__":

    # # Multile ins run
    # ins_res = [f"Hyd_{x}" for x in range(37)]
    # exps = [f"out230914_i37g500_b_jp/{i}" for i in ins_res]
    # for exp in exps:
    #     rm = make_reader(False, exp)
    #     for x in [0,]:
    #         sio_to_cf(rm, "cmass_loss_cav", x)

    exps = argv[1:] # Name of the experiment folder
    dset = "sio_reader"
    pfts = [0,1,-1] # Can be a range of len(reader.pft_list) or a list of pft numbers

    for exp in exps:
        rd = make_reader(dset, "Annually", exp)
        for x in pfts:
            sio_to_cf(rd, "cmass_loss_bg", x, nc_out, bbox=pan_amazon)
            sio_to_cf(rd, "cveg", x, nc_out, bbox=pan_amazon)
    rd.close()


    # for exp in exps:
    #     rm = make_reader(dset, "Monthly", exp)
    #     for x in pfts:

    #         sio_to_cf(rm, "et", x, nc_out)
    #         sio_to_cf(rm, "npp", x, nc_out)
    #         sio_to_cf(rm, "gpp", x, nc_out)
    #         sio_to_cf(rm, "ar", x, nc_out)
    #         sio_to_cf(rm, "wstress", x, nc_out)
    # rm.close()
