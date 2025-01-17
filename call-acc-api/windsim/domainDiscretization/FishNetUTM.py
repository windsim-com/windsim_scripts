import geopandas as gpd
from shapely import geometry
import numpy as np

class FishNetUTM:
    @staticmethod
    def createFishnet(shapefile, square_size_km:32,overlap_km = 0,refinement_km=30):
        # Read the shapefile
        gdf = gpd.read_file(shapefile)

        # Determine UTM zone based on shapefile's centroid
        centroid = gdf.geometry.unary_union.centroid
        utm_zone = int(np.floor((centroid.x + 180) / 6) + 1)
        utm_crs = f"EPSG:326{utm_zone}"  # Northern hemisphere

        # Reproject to UTM coordinate system
        gdf = gdf.to_crs(utm_crs)
        square_size = square_size_km * 1000
        # Get the extent of the shapefile in UTM coordinates
        minX, minY, maxX, maxY = gdf.total_bounds
        refinement_size = refinement_km * 1000
        # Create a fishnet
        x, y = (minX, minY)
        geom_array = []
        overlap_size = overlap_km * 1000


        # # Create squares in UTM units (meters) with overlap
        while y <= maxY:
            while x <= maxX:
                geom = geometry.Polygon(
                    [(x, y), (x, y + square_size), (x + square_size, y + square_size), (x + square_size, y), (x, y)]
                )
                geom_array.append(geom)
                x += (square_size - overlap_size)
            x = minX
            y += (square_size - overlap_size)

        # Select only the intersecting cells
        intersecting_cells = []
        # Select only the intersecting cells and calculate refinement area
        subdomains = []
        for poly in geom_array:
            if any(poly.intersects(geom) for geom in gdf.geometry):
                intersecting_cells.append(poly)
                # Center of the current cell
                centroid_subdomain = poly.centroid
                center_x = centroid_subdomain.x
                center_y = centroid_subdomain.y
                 = poly.centroid
                # Calculate refinement area
                half_refinement = refinement_size / 2
                refinement_geom = geometry.Polygon([
                    (center_x - half_refinement, center_y - half_refinement),
                    (center_x - half_refinement, center_y + half_refinement),
                    (center_x + half_refinement, center_y + half_refinement),
                    (center_x + half_refinement, center_y - half_refinement),
                    (center_x - half_refinement, center_y - half_refinement)
                ])

                # Store subdomain and refinement area
                ext = poly.exterior.coords.xy
                subdomain_coords = [{"latitude": lat, "longitude": lon} for lat, lon in zip(ext[1], ext[0])]

                ref_ext = refinement_geom.exterior.coords.xy
                refinement_coords = [{"latitude": lat, "longitude": lon} for lat, lon in zip(ref_ext[1], ref_ext[0])]

                subdomains.append({
                    "subdomain": subdomain_coords,
                    "refinement_area": refinement_coords
                })

        # Create a GeoDataFrame with the intersecting grid
        #complete_fishnet = gpd.GeoDataFrame(geometry=intersecting_cells, crs=utm_crs)


        # Save the resulting fishnet to a new shapefile
        #complete_fishnet.to_file('complete_fishnet_grid_optimized.shp')
        # Optionally plot to visualize the subdomains and refinement areas
        #complete_fishnet = gpd.GeoDataFrame(geometry=intersecting_cells, crs=utm_crs)

        # fig, ax = plt.subplots(figsize=(10, 10))
        # gdf.boundary.plot(ax=ax, color='blue', linewidth=1, label='Original Geometry')
        # Plot total domain and refinement areas
        # for subdomain in subdomains:
        #     sim_geom = geometry.Polygon(
        #         [(coord['longitude'], coord['latitude']) for coord in subdomain['subdomain']]
        #     )
        #     refinement_geom = geometry.Polygon(
        #         [(coord['longitude'], coord['latitude']) for coord in subdomain['refinement_area']]
        #     )
        #     gpd.GeoSeries([refinement_geom]).boundary.plot(ax=ax, color='green', linewidth=0.5, linestyle=':')
        #     gpd.GeoSeries([sim_geom]).boundary.plot(ax=ax, color='red', linewidth=0.5, linestyle=':')

        return subdomains, centroids


    #subdomains, centroid = createFishnet("C:/Users/TorsteinSaeter/source/repos/ShapeFileToFishnet/StantecAreas/StantecAreas.shp", square_size=32000, overlap_km=2,refinement_km= 30)

    # Example usage:
    #createFishnet("path_to_your_shapefile.shp")
    #createFishnet("C:/Users/TorsteinSaeter/source/repos/ShapeFileToFishnet/Stantec5/StantecAreas.shp")
