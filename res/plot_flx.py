import os
import matplotlib.pyplot as plt
from reader import make_reader

DPI = 100

experiment = "./fluxnet_out00"

os.makedirs("./FIGS", exist_ok=True)

def comp(pfn=0, comp=True):

    new = make_reader(dset="FLUXNET2015", exp=experiment, time_int="Monthly")
    pfts = new.pft_list

    keys = ["gpp", "et"] if comp else ["nee", "reco"]


    for grd in range(len(new.GRIDLIST)):
        # Read data
        v1 = new.make_df(variables=[keys[0],], gridcell=grd, pft_number=pfn)
        v2 = new.make_df(variables=[keys[1],], gridcell=grd, pft_number=pfn)

        v1_ref = new.get_ref_var(keys[0], gridcell=grd)
        v2_ref = new.get_ref_var(keys[1], gridcell=grd) # TODO change aet to et in FLUXNET_EU repo

        # PLOT
        fig, axs = plt.subplots(ncols=1, nrows=2, sharex=True)

        axs[0].set_title(f"{new.GRIDLIST[grd][-1]} - FLUXNET2015 - {pfts[pfn]}")

        v1.plot(ax=axs[0], color="g")
        v1_ref.plot(ax=axs[0], color="r", linestyle='dashed')
        v2.plot(ax=axs[1], color="b")
        v2_ref.plot(ax=axs[1], color="r", linestyle='dashed')


        axs[0].set_ylabel(f" {keys[0].upper()} ({new.var_units['gpp']})")

        axs[1].set_ylabel(f" {keys[1].upper()} ({new.var_units[keys[1]]})")
        axs[1].legend(["MOD","REF"])

        if not comp:
            # PLot hr and ar
            hr  = new.make_df("hr", grd, pfn)
            ar  = new.make_df("ar", grd, pfn)
            hr.plot(ax=axs[1], color="chocolate", linestyle='dashed')
            ar.plot(ax=axs[1], color="darkcyan", linestyle='dashed')
            axs[1].legend(["MOD","REF", 'hr','ar'])
        else:
            axs[1].legend(["MOD","REF"])

        plt.savefig(fname=f"./FIGS/{''.join(keys)}_{new.GRIDLIST[grd][-1]}_{pfts[pfn]}.png", dpi=500)
        plt.clf()
        plt.close(fig)
    new.close()
