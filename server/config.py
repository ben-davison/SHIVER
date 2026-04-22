# server/config.py
import platform
from pathlib import Path

current_os = platform.system()

if current_os == "Windows":
    base_path_gr = Path("R:/aux_data/overlays/Greenland")
    base_path_ant = Path("R:/aux_data/overlays/Antarctica")
    overlay_path_gr = Path("R:/aux_data/overlays/Greenland")
    overlay_path_ant = Path("R:/aux_data/overlays/Antarctica")
    landsat_mosaic_path_gr = Path("R:/aux_data/image_mosaic/Greenland/GEE_S2/greenland_tiles_20m")
    ZARR_PATHS = {
        "Greenland": Path("R:/SCADI/output/Sentinel1/Greenland/mosaic/subregions/lev/Greenland_multisource_speed.zarr"),
        "Antarctica": Path("R:/SCADI/output/Sentinel1/Antarctica/mosaic/subregions/peninsula/Antarctica_multisource_speed.zarr")
    }
    COG_BASE_DIR = {
        "Greenland": Path("R:/aux_data/overlays/Greenland"),
        "Antarctica": Path("R:/aux_data/overlays/Antarctica")
    }
else:
    base_path_gr = Path("/mnt/grio1/Shared/SHIVER/data/Greenland")
    base_path_ant = Path("/mnt/grio1/Shared/SHIVER/data/Antarctica")
    overlay_path_gr = Path("/mnt/grio1/Shared/SHIVER/data/Greenland/overlays")
    overlay_path_ant = Path("/mnt/grio1/Shared/SHIVER/data/Antarctica/overlays")
    landsat_mosaic_path_gr = Path("/mnt/grio1/Shared/SHIVER/data/Greenland/image_mosaic/greenland_tiles_20m")
    ZARR_PATHS = {
        "Greenland": Path("/mnt/grio1/Shared/SHIVER/data/Greenland/Greenland_multisource_speed.zarr"),
        "Antarctica": Path("/mnt/grio1/Shared/SHIVER/data/Antarctica/Antarctica_multisource_speed.zarr")
    }
    COG_BASE_DIR = {
        "Greenland": Path("/mnt/grio1/Shared/SHIVER/data/Greenland/overlays"),
        "Antarctica": Path("/mnt/grio1/Shared/SHIVER/data/Antarctica/overlays")
    }

TIFF_PATHS = {
    "Greenland": {
        "default_speed": overlay_path_gr / "Greenland_Speed_Hillshaded_COG.tif",
        "u"    : overlay_path_gr / "Greenland_U_Merged_COG.tif", 
        "v"    : overlay_path_gr / "Greenland_V_Merged_COG.tif", 
        "count": overlay_path_gr / "Greenland_AllSources_Epoch_Count.tif",
        "trend": overlay_path_gr / "Greenland_AllSources_Linear_Trend_masked.tif",
        "hillshade": overlay_path_gr / "Greenland_Hillshade_COG.tif",
        "range": overlay_path_gr / "Greenland_Ensemble_Median_Spread_COG.tif",
        "landsat_mosaic": landsat_mosaic_path_gr / "greenland_20m_mosaic.vrt"
    },
    "Antarctica": {
        "default_speed": overlay_path_ant / "Antarctica_Speed_Hillshaded_COG.tif",
        "u":     overlay_path_ant / "Antarctica_U_Merged_COG.tif", 
        "v":     overlay_path_ant / "Antarctica_V_Merged_COG.tif", 
        "count": overlay_path_ant / "Antarctica_AllSources_Epoch_Count.tif",
        "trend": overlay_path_ant / "Antarctica_AllSources_Linear_Trend_masked.tif",
        "hillshade": overlay_path_ant / "Antarctica_Hillshade_COG.tif",
        "range": overlay_path_ant / "Antarctica_Ensemble_Median_Spread.tif",
    }
}
    