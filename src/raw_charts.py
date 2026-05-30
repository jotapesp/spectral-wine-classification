import utils
import os

base_path = os.path.dirname(__file__)
file_path = os.path.join(base_path, '../data/Wine_FTIR_Triplicate_Spectra.csv')
df = utils.load_data(utils.file_path)

utils.plot_raw_triplicate_scatter(df[['Wine_01_Cab_Rep1']])
utils.plot_raw_triplicate_scatter(df[['Wine_01_Cab_Rep2']])
utils.plot_raw_triplicate_scatter(df[['Wine_01_Cab_Rep3']])