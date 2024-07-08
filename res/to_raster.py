import argparse

from reader import make_reader
from writer import sio_to_cf

def main():
    parser = argparse.ArgumentParser(description="Convert LPJ-GUESS smart output to CF compliant netCDF files")
    parser.add_argument("experiments", nargs="+", help="Name(s) of the experiment folder(s)")
    parser.add_argument("--var", help="Variable to convert to netCDF files")
    parser.add_argument("--time_int", default="Annually",
                        help="Time integration: 'Daily', 'Monthly', or 'Annually'")
    parser.add_argument("--variables", nargs="+", default=["cmass_loss_bg", "cveg"],
                        help="List of variables to convert to netCDF files")
    parser.add_argument("--pfts", type=int,nargs="+", default=[-1],
                        help="Can be a range of len(reader.pft_list) or a list of pft numbers. -1 Default to total of all PFTs")
    parser.add_argument("--nc_out", default="./cf_outputs", help="Output folder for netCDF files")
    parser.add_argument("--region", default="pan_amazon", help="Bounding box for the region of interest")
    args = parser.parse_args()

    if args.region == "pan_amazon" or args.region == "pan-amazon":
        from geo import pan_amazon as region
    else:
        from geo import global_region as region


    for exp in args.experiments:
        rd = make_reader(time_int = args.time_int, exp=exp)
        for pft in args.pfts:
            sio_to_cf(rd, args.var, pft, args.nc_out, region=region)
        rd.close()


if __name__ == "__main__":
    main()



# nc_out = "./cf_outputs"

# exps = argv[1:] # Name of the experiment folder
# dset = "sio_reader"
# pfts = [0,1,-1] # Can be a range of len(reader.pft_list) or a list of pft numbers

# for exp in exps:
#     rd = make_reader(dset, "Annually", exp)
#     for pft in pfts:
#         sio_to_cf(rd, "cmass_loss_bg", pft, nc_out, bbox=pan_amazon)
#         sio_to_cf(rd, "cveg", pft, nc_out, bbox=pan_amazon)
#     rd.close()



    # # Multile ins run
    # ins_res = [f"Hyd_{x}" for x in range(37)]
    # exps = [f"out230914_i37g500_b_jp/{i}" for i in ins_res]
    # for exp in exps:
    #     rm = make_reader(False, exp)
    #     for x in [0,]:
    #         sio_to_cf(rm, "cmass_loss_cav", x)




    # for exp in exps:
    #     rm = make_reader(dset, "Monthly", exp)
    #     for x in pfts:

    #         sio_to_cf(rm, "et", x, nc_out)
    #         sio_to_cf(rm, "npp", x, nc_out)
    #         sio_to_cf(rm, "gpp", x, nc_out)
    #         sio_to_cf(rm, "ar", x, nc_out)
    #         sio_to_cf(rm, "wstress", x, nc_out)
    # rm.close()
