import os

import astropy.units as u
import h5py
import numpy as np
import sunpy.map as smap
from sunpy.net import Fido, attrs as a
import matplotlib.pylab as plt
import re


def down_aia_304():
    dfl1 = os.listdir('/media/temp/yqwei/suntoday_dem_2018_2021')
    dfl2 = os.listdir('/media/temp/yqwei/sun_today_dem')
    dfl = dfl1 + dfl2
    aia_dates = []
    for cf in dfl:
        cdate = os.path.basename(cf)[8:18].replace('-', '/')
        ct1 = cdate + ' 23:00'
        ct2 = cdate + ' 23:01'
        aia_dates.append(a.Time(ct1, ct2))
    for aia_time in aia_dates:
        result = Fido.search(aia_time, a.Instrument.aia, a.Wavelength(304 * u.angstrom), a.Sample(24 * u.hour))
        #downloaded_files = Fido.fetch(result, path='/Users/walterwei/Downloads/work/fasr_simulation/aia_304')
        downloaded_files = Fido.fetch(result, path='/media/temp/yqwei/aia_304')
        print(f"Downloaded data for {aia_time}")


def aia304_to_chormo(date_str, plot_it=False):
    # aiafile = ut.makelist(tdir='/Users/walterwei/Downloads/work/fasr_simulation/aia_304/', keyword1=date_str, keyword2='fits')[0]
    aia304_path = '/media/temp/yqwei/aia_304/'
    aiafile = os.listdir(aia304_path)
    arcsec2rad = 1 / 3600. * np.pi / 180
    solarrad = 16 * 60  ##arcsec

    # aiamap=med_filt(smap.Map(aiafile))
    aiamap = smap.Map(aiafile)

    # check the new_dimensions carefully!
    new_dimensions = [2048, 2048] * u.pixel
    # new_dimensions = [2048,2048] * u.pixel
    aiamap = aiamap.resample(new_dimensions)

    aiadata = aiamap.data

    aiadata[aiadata < -10] = np.nan

    tot_flux = np.nansum(aiadata)

    omega_sun = np.pi * (solarrad * arcsec2rad) ** 2
    omega_pix = (aiamap.meta['cdelt1'] * arcsec2rad) ** 2

    tb_data = 10880.0 * omega_sun / omega_pix * aiadata / tot_flux
    aiamap.meta['pixlunit'] = 'Tb'

    tbmap = smap.Map(tb_data, aiamap.meta)
    tbmap.plot_settings['title'] = 'Chromospheric Tb contribution'

    hf = h5py.File(
        #'/Users/walterwei/Downloads/work/fasr_simulation/chromo/chromospheric_tbmap_{}.hdf5'.format(date_str), "w")
        '/media/temp/yqwei/aia_304/chromospheric_tbmap_{}.hdf5'.format(date_str), "w")
    keys = tbmap.meta.keys()

    for key in keys:
        if key != 'keycomments':
            hf.attrs[key] = tbmap.meta[key]
    tbmap.data[np.isnan(tbmap.data)] = 0.0
    hf.create_dataset('tb', data=tbmap.data)


    hf.close()
    if plot_it:
        fig = plt.figure()
        ax = fig.add_subplot(121, projection=tbmap)
        # tbmap.plot('sdoaia304', axes=ax)
        tbmap.plot()
        plt.colorbar()

        ax = fig.add_subplot(122, projection=aiamap)
        # aiamap.plot('sdoaia304', axes=ax)
        aiamap.plot()
        plt.show()

def make_chromo_emission():
    from utils import makelist
    aia_304_list = makelist(tdir='/media/temp/yqwei/aia_304/', keyword1='fits')
    date_list = []
    for cfits in aia_304_list:
        match = re.search(r'\d{4}_\d{2}_\d{2}', cfits)
        date_str = match.group(0)
        date_list.append(date_str)
    import multiprocessing
    with multiprocessing.Pool(processes=3) as pool:
        # Map the function to the inputs in parallel
        results = pool.map(aia304_to_chormo, date_list)
        pool.join()
        pool.close()

def main():
    down_aia_304()
    make_chromo_emission()
    #aia304_to_chormo()


if __name__ == "__main__":
    main()
