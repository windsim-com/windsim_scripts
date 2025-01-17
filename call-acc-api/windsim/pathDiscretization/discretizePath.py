import geopandas as gpd
from shapely import geometry
import numpy as np
class discretizePath:
    @staticmethod
    def discretize_path_with_squares(shapefile, interval_km=30, square_side_km=15):
        # Load the shapefile using Geopandas
        gdf = gpd.read_file(shapefile)
        
        # Determine recommended UTM zone based on the path's centroid
        centroid = gdf.geometry.iloc[0].centroid
        utm_zone = int(np.floor((centroid.x + 180) / 6) + 1)
        utm_crs = f"EPSG:326{utm_zone}"  # Northern hemisphere UTM

        # Reproject the geometries to the UTM coordinate system
        gdf = gdf.to_crs(utm_crs)
        
        # Assuming there is one LineString geometry in the shapefile
        line = gdf.geometry.iloc[0]
        
        # Convert km to meters
        interval_m = interval_km * 1000
        half_square_side_m = square_side_km * 1000

        # Create lists to store the points and polygons
        subdomains = []

        # Initialize distance along the line
        current_distance = 0.0
        # Loop to generate points and square polygons
        while current_distance < line.length:
            # Get point at current distance
            point = line.interpolate(current_distance)
            # Create a bounding box centered on this point
            poly=geometry.Polygon([
                (point.x - half_square_side_m, point.y - half_square_side_m),
                (point.x - half_square_side_m, point.y + half_square_side_m),
                (point.x + half_square_side_m, point.y + half_square_side_m),
                (point.x + half_square_side_m, point.y - half_square_side_m),
                (point.x - half_square_side_m, point.y - half_square_side_m)
            ])

            # Increment distance
            current_distance += interval_m
            ext = poly.exterior.coords.xy
            subdomain_coords = [{"latitude": lat, "longitude": lon} for lat, lon in zip(ext[1], ext[0])]
            refinement_coords = subdomain_coords
            subdomains.append({
                "subdomain": subdomain_coords,
                "refinement_area": refinement_coords,
                "centroid_subdomain":[point.y,point.x]
                    })
        return subdomains
