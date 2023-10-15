import json
import matplotlib.pyplot as plt
import db_connection 
import turtle
import math
import random
from tkinter import PhotoImage
import turtle
import math
import random
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import Voronoi
from scipy import ndimage
import cv2
import os
import sqlite3

# Instncing this class results in all images being saved to their respective folders. Beyond init, it doesnt do anything else (yet)
class Island():
    __map_path:str=None
    __outline=None
    __color_map:{}={}
    def __init__(self) -> None:
        self.__map_path="img/map"
        turtle.setup(1100,1100)
        turtle.title("Random Island Generator - PythonTurtle.Academy")
        turtle.speed(0)
        turtle.hideturtle()
        turtle.tracer(0,0)    
        turtle.bgcolor('royal blue')
        turtle.pencolor('green')
        turtle.fillcolor('forest green')
        turtle.begin_fill()
        self.shoreline(-300,0,300,0,0.55) # call recursion
        self.shoreline(300,0,-300,0,0.55) # call recursion
        turtle.end_fill()
        turtle.update()
        cv = turtle.getcanvas()
        cv.postscript(file=self.map_path(False), colormode='color')
        self.convert_to_png(self.map_path(False), self.map_path())
        self.flood_fill_centre()
        self.color_outer_green_to_yellow()
        self.color_white_to_blue()
        self.generate_voronoi_noise()
        self.replace_green_with_noise()
        self.save_color_blocks()
        self.split_color_block_by_color()

    def map_path(self, is_bmp=True):
        map_temp=self.__map_path
        if(is_bmp):
            map_temp+=".png"
        else:
            map_temp+=".ps"
        return map_temp

    @staticmethod
    def convert_to_png(ps_path, output_path):
        with open(ps_path, 'r') as ps_file:
            lines = ps_file.readlines()
        points = []
        for line in lines:
            if "lineto" in line:
                coordinates = line.split()[:2]
                if len(coordinates) == 2:
                    try:
                        x, y = map(float, coordinates)
                        points.append((x, y))
                    except ValueError:
                        pass

        min_x = min(point[0] for point in points)
        max_x = max(point[0] for point in points)
        min_y = min(point[1] for point in points)-100
        max_y = max(point[1] for point in points)+100

        width = int(max_x - min_x) + 1
        height = int(max_y - min_y) + 1
        canvas = np.zeros((height, width, 3), dtype=np.uint8) + 255  # Initialize with white (255, 255, 255)
        draw = ImageDraw.Draw(Image.fromarray(canvas))
        current_x, current_y = None, None
        transformed_coordinates = []
        for x, y in points:
            transformed_x = int(x - min_x)
            transformed_y = int(y - min_y)
            transformed_coordinates.append((transformed_x, transformed_y))
        line_image = Image.new('RGB', (width, height), (255, 255, 255))
        draw_lines = ImageDraw.Draw(line_image)
        for i in range(1, len(transformed_coordinates) - 1): 
            x, y = transformed_coordinates[i]
            x_offset = 80  # Adjust this value as needed
            y_offset = -20  # Adjust this value as needed
            x -= x_offset
            y -= y_offset
            if current_x is not None and current_y is not None and abs(x - current_x) < 2 and abs(y - current_y) < 2:
                draw_lines.line(
                    [(current_x, current_y), (x, y)],
                    fill=(0, 255, 0), width=2
                )
            current_x, current_y = x, y
        canvas_image = Image.fromarray(canvas)
        canvas_image.paste(line_image, (0, 0))
        x_offset = (width - canvas_image.width) // 2
        y_offset = (height - canvas_image.height) // 2
        centered_canvas = np.zeros((height, width, 3), dtype=np.uint8) + 255  # Initialize with white (255, 255, 255)
        centered_canvas[y_offset:y_offset + canvas_image.height, x_offset:x_offset + canvas_image.width] = canvas_image
        final_canvas_image = Image.fromarray(centered_canvas)
        final_canvas_image.save(output_path, 'PNG')
        
    @staticmethod
    def draw_line(x1,y1,x2,y2): # function to draw line
        turtle.up()
        turtle.goto(x1,y1)
        turtle.down()
        turtle.goto(x2,y2)

    @staticmethod
    def dist(p1,p2): # Euclidean distance betwen p1 and p2
        return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

    def shoreline(self,x1,y1,x2,y2,ratio): # recurisve function to draw the shoreline
        L = self.dist((x1,y1),(x2,y2))
        if L <= 1: # distance is short enough, directly draw the line
            self.draw_line(x1,y1,x2,y2)
            return
        rs = ratio + random.uniform(-0.1,0.1) # let ratio flucuate slightly around the chosen value
        rs = max(0.5,rs) # make sure ratio stays at least half of the length
        midx = (x1+x2)/2 # center of ellipse
        midy = (y1+y2)/2    
        rx = L/2 + (2*rs-1)/2*L # width of ellipse
        ry = ((L*rs)**2 - (L/2)**2)**0.5 # height of ellipse
        theta = math.atan2(y2-y1,x2-x1) # the tilt angle of ellipse
        alpha = random.uniform(math.pi*0.3,math.pi*0.7) # flucuate around math.pi/2
        x3 = rx*math.cos(alpha)*math.cos(theta) - ry*math.sin(alpha)*math.sin(theta) + midx # parametric equation for ellipse
        y3 = rx*math.cos(alpha)*math.sin(theta) + ry*math.sin(alpha)*math.cos(theta) + midy
        self.shoreline(x1,y1,x3,y3,ratio) # do this recursively on each segment
        self.shoreline(x3,y3,x2,y2,ratio)

    def flood_fill_centre(self):
        image_blob = None
        with Image.open(self.map_path()) as image:
            image_blob = np.array(image)
        self.__outline=np.copy(image_blob)
        x, y, _ = image_blob.shape
        
        x_center, y_center = x // 2, y // 2
        unfilled_pixels = [(x_center, y_center)]
        target_color = [255, 255, 255]
        replacement_color = [0, 255, 0]
        while unfilled_pixels:
            pixel = unfilled_pixels.pop()
            xpix, ypix = pixel
            if (xpix >= 0 and xpix < x) and (ypix >= 0 and ypix < y) and not np.array_equal(image_blob[xpix, ypix], replacement_color):
                if np.array_equal(image_blob[xpix, ypix], target_color):
                    image_blob[xpix, ypix] = replacement_color
                    unfilled_pixels.extend([(xpix - 1, ypix), (xpix + 1, ypix), (xpix, ypix - 1), (xpix, ypix + 1)])
        modified_image = Image.fromarray(image_blob)
        modified_image.save(self.map_path())
        return None

    def color_outer_green_to_yellow(self):
        path = self.map_path()
        with Image.open(path) as im:
            image_blob = np.array(im)

        target_color = [0, 255, 0]  # Green
        outline_color = [255, 255, 0]  # Yellow (outline color)

        # Iterate through the pixels of the outline image
        for xpix in range(image_blob.shape[0]):
            for ypix in range(image_blob.shape[1]):
                if np.array_equal(self.__outline[xpix, ypix], target_color):
                    # If the pixel in the outline is green, draw a yellow pixel in the original image
                    image_blob[xpix, ypix] = outline_color

        modified_image = Image.fromarray(image_blob)
        modified_image.save(path)
        return None

    def color_white_to_blue(self):
        path = self.map_path()
        with Image.open(path) as im:
            image_blob = np.array(im)

        white_color = [255, 255, 255]  # White
        blue_color = [0, 0, 255]  # Blue

        # Iterate through the pixels of the image
        for xpix in range(image_blob.shape[0]):
            for ypix in range(image_blob.shape[1]):
                if np.array_equal(image_blob[xpix, ypix], white_color):
                    # If the pixel is white, change it to blue
                    image_blob[xpix, ypix] = blue_color

        modified_image = Image.fromarray(image_blob)
        modified_image.save(path)
        return None

    def generate_voronoi_noise(self):
        if self.__outline is None:
            with Image.open(self.map_path()) as im:
                self.__outline = np.array(im)
        width, height, _ = self.__outline.shape
        num_colors = 6  # Adjust the number of colors as needed
        colors = np.random.randint(0, 256, size=(num_colors, 3), dtype=np.uint8)
        num_points = width * height // 10000  # Adjust the density as needed
        points = np.random.randint(0, max(width, height), size=(num_points, 2))
        vor = Voronoi(points)
        voronoi_image = np.zeros((width, height, 3), dtype=np.uint8)
        for region_idx, region in enumerate(vor.regions):
            if not -1 in region and len(region) > 0:
                polygon = [vor.vertices[i] for i in region]
                polygon = np.array(polygon, dtype=int)
                color = tuple(map(int, colors[region_idx % num_colors]))
                cv2.fillPoly(voronoi_image, [polygon], color)
        modified_image = Image.fromarray(voronoi_image)
        modified_image.save("img/noise.png")

    def replace_green_with_noise(self):
        img_path = self.map_path()
        with Image.open(img_path) as im:
            original_image = np.array(im)

        noise_image_path = "img/noise.png"
        with Image.open(noise_image_path) as im:
            noise_image = np.array(im)

        green_color = [0, 255, 0]

        land_mask = []

        for xpix in range(original_image.shape[0]):
            for ypix in range(original_image.shape[1]):
                if np.array_equal(original_image[xpix, ypix], green_color):
                    land_mask.append((xpix, ypix))
                    voronoi_color = noise_image[xpix, ypix]

                    mixing_factor = 0.6  

                    mixed_color = ((original_image[xpix, ypix] * (1 - mixing_factor)) + voronoi_color * mixing_factor).astype(np.uint8)
                    original_image[xpix, ypix] = mixed_color

        self.__outline = list.copy(land_mask)
        modified_image = Image.fromarray(original_image)
        modified_image.save(img_path)

    def internal_blank_pattern(self):
        img_path = self.map_path()
        with Image.open(img_path) as im:
            original_image = np.array(im)

        noise_image_path = "img/noise.png"
        with Image.open(noise_image_path) as im:
            noise_image = np.array(im)

        # Define the green color you want to replace
        green_color = [0, 255, 0]

        # Define a set of replacement colors without alpha
        replacement_colors = [
            [255, 0, 0],    # Red
            [0, 0, 255],    # Blue
            [255, 255, 0],  # Yellow
            [255, 0, 255],  # Magenta
            [0, 255, 255],  # Cyan
            [255, 128, 0],  # Orange
            [128, 0, 255],  # Purple
            [128, 128, 0],  # Olive
        ]

        land_mask = []
        replacement_color_index = 0  # Start with the first replacement color

        for xpix in range(original_image.shape[0]):
            for ypix in range(original_image.shape[1]):
                if np.array_equal(original_image[xpix, ypix], green_color):
                    land_mask.append((xpix, ypix))
                    voronoi_color = noise_image[xpix, ypix]
                    # Use the replacement color based on the index
                    replacement_color = replacement_colors[replacement_color_index]
                    replacement_color_index = (replacement_color_index + 1) % len(replacement_colors)  # Cycle through colors

                    voronoi_color[:3] = replacement_color  # Set RGB channels

                    # Modify the mixed_color as needed
                    mixed_color = ((original_image[xpix, ypix] * 2) + voronoi_color) // 2
                    original_image[xpix, ypix] = mixed_color

        self.__outline = list.copy(land_mask)
        modified_image = Image.fromarray(original_image)
        modified_image.save(img_path)
        
    def save_color_blocks(self):
        img_path = self.map_path()
        with Image.open(img_path) as im:
            original_image = np.array(im)
        non_bw_mask = np.any((original_image != 0) & (original_image != 255), axis=-1)
        labeled_mask, num_features = ndimage.label(non_bw_mask)
        os.makedirs("color_blocks", exist_ok=True)
        for i in range(1, num_features + 1):
            feature_mask = labeled_mask == i
            color_block = np.zeros_like(original_image)
            color_block[feature_mask] = original_image[feature_mask]
            color_block_image = Image.fromarray(color_block)  # Convert to Image
            block_path = os.path.join("color_blocks", f"color_block_{i}.png")
            color_block_image.save(block_path)
            color_block_array = np.array(color_block_image)  # Convert to NumPy array
            unique_colors = np.unique(color_block_array.reshape(-1, color_block_array.shape[2]), axis=0)
            for color in unique_colors:
                color_mask = np.all(color_block_array == color, axis=-1)
                labeled_mask, num_features = ndimage.label(color_mask)
                for j in range(1, num_features + 1):
                    feature_mask = labeled_mask == j


        
    def split_color_block_by_color(self, image_path="color_blocks/color_block_1.png"):
        index=1
        with Image.open(image_path) as im:
            color_block_image = np.array(im)
        unique_colors = np.unique(color_block_image.reshape(-1, color_block_image.shape[2]), axis=0)
        split_blocks_dir = "split_color_blocks"
        with open("terrain-archetypes.json", "r") as archetype_file:
            archetype_data = json.load(archetype_file)
        archetype_names = list(archetype_data.keys())
        os.makedirs(split_blocks_dir, exist_ok=True)
        for file in os.listdir(split_blocks_dir):
            file_path = os.path.join(split_blocks_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")
        with open("terrain-archetypes.json", "r") as archetype_file:
            archetype_data = json.load(archetype_file) 
        archetype_names = list(archetype_data.keys())
        i = 0  # Counter for i
        terrain_data = {}  # Initialize the terrain data dictionary
        for color in unique_colors:
            color_mask = np.all(color_block_image == color, axis=-1)
            labeled_mask, num_features = ndimage.label(color_mask)
            self.__color_map[self.color_to_string(color)] = archetype_names[i % len(archetype_names)]
            j = 0  # Counter for j
            for j in range(1, num_features + 1):
                feature_mask = labeled_mask == j
                land_size=np.sum(feature_mask)
                if  land_size< 200 or (j==1 and i==0):  
                    continue
                split_color_area = np.zeros((color_block_image.shape[0], color_block_image.shape[1], 4), dtype=np.uint8)
                split_color_area[feature_mask, :3] = color_block_image[feature_mask, :3]  # Extract color data
                split_color_area[feature_mask, 3] = 255  # Set alpha to fully opaque
                archetype_color = np.mean(split_color_area[feature_mask, :3], axis=0).astype(int)
                color_str = self.color_to_string(color)
                if color_str in self.__color_map:
                    archetype_name = self.__color_map[color_str]
                else:
                    archetype_names = list(archetype_data.keys())
                    archetype_name = random.choice(archetype_names)
                    self.__color_map[color_str] = archetype_name
                print("terrain: "+str(archetype_data[self.__color_map[color_str]]["name"]) + "  colour" + str(archetype_color))
                terrain_data[index] = {
                    "name": archetype_data[self.__color_map[color_str]]["name"],
                    "temperature": int(archetype_data[self.__color_map[color_str]]["temperature"]),
                    "precipitation": int(archetype_data[self.__color_map[color_str]]["precipitation"]),
                    "vegetation_density": int(archetype_data[self.__color_map[color_str]]["vegetation_density"]),
                    "terrain_type": self.__color_map[color_str],
                    "area": int(land_size),  # Convert land_size to integer
                    "color": color[:3].tolist()
                }
                index+=1
                border_mask = np.zeros(color_block_image.shape[:2], dtype=bool)
                for x in range(1, color_block_image.shape[0] - 1):
                    for y in range(1, color_block_image.shape[1] - 1):
                        if feature_mask[x, y]:
                            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                                if not feature_mask[x + dx, y + dy]:
                                    border_mask[x, y] = True
                border_pixels = split_color_area[border_mask]
                split_color_area[border_mask, :3] = (border_pixels[:, :3] * 0.8).astype(np.uint8)
                split_area_image = Image.fromarray(split_color_area)
                block_path = os.path.join(split_blocks_dir, f"split_block_{i}_area_{j}.png")
                split_area_image.save(block_path)
                j += 1  # Increment j for the next fragment
            i += 1  # Increment i for the next color
        with open('terrain.json', 'w') as json_file:
            json.dump(terrain_data, json_file, indent=4)


    @staticmethod
    def color_to_string(color):
        return f"{color[0]},{color[1]},{color[2]}"
   

    # Worth doing? some kind of post-process is needed. The image is generated in low res.
    def scale_images_in_folder(self, folder_path):
        files = os.listdir(folder_path)
        for file in files:
            if file.lower().endswith(".png"):
                file_path = os.path.join(folder_path, file)
                with Image.open(file_path) as img:
                    target_width = 1920
                    target_height = 1080
                    current_width, current_height = img.size
                    scaling_factor_w = target_width / current_width
                    scaling_factor_h = target_height / current_height
                    scaling_factor = min(scaling_factor_w, scaling_factor_h)
                    new_width = int(current_width * scaling_factor)
                    new_height = int(current_height * scaling_factor)
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    img.save(file_path)

class MapUtils():
    def draw_ocean(self):
        width,height=Image.open("img/map.png").size
        image = Image.new('RGB', (width, height), 'black')
        draw = ImageDraw.Draw(image)
        for _ in range(4000):  # Increase the number of waves for chaos
            x = random.randint(0, width)
            y = random.randint(0, height)  # Allow waves at any height
            wave_size = random.randint(60, 60)  # Vary the size of the waves
            wave_color = (0, 0, random.randint(0, 80))  # Vary the shade of blue
            draw.ellipse((x, y, x + wave_size, y + wave_size), fill=wave_color)
        wavy_image = Image.new('RGB', (width, height))
        for x in range(width):
            for y in range(height):
                angle = math.sin(2 * math.pi * x / 60)  # Adjust the frequency and amplitude
                new_x = int(x + 20 * angle)
                if 0 <= new_x < width:
                    pixel = image.getpixel((new_x, y))
                    wavy_image.putpixel((x, y), pixel)
        def create_distortion_pattern(width, height):
            distortion_image = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(distortion_image)
            for x in range(width):
                for y in range(height):
                    offset_x = int(10 * math.sin(2 * math.pi * x / 40))
                    offset_y = int(10 * math.sin(2 * math.pi * y / 40))
                    if 0 <= x + offset_x < width and 0 <= y + offset_y < height:
                        pixel = wavy_image.getpixel((x + offset_x, y + offset_y))
                        pixel = tuple(int(val * 0.2) for val in pixel)
                        distortion_image.putpixel((x, y), pixel)
            return distortion_image
        
        
        distortion_pattern = create_distortion_pattern(width, height)
        result_image = Image.blend(wavy_image, distortion_pattern, alpha=0.5)
        result_image.save("img/ocean/"+str(0)+'.png')

class AnimalData():
    __conn=None
    def __init__(self) -> None:
        self.__conn=sqlite3.connect('animal_database.db')
    @staticmethod
    def load_json_data(path):
        try:
            with open(path, "r") as json_data:
                data=json.load(json_data)
        except:
            data=None
        return data

    def get_animals_by_region(self, region:int):
        summary:str=""
        try:
            animal_data=self.load_json_data('animals.json')
            animal_names = []  
            for animal_name, animal_attributes in animal_data.items():
                animal_names.append(animal_name)
            if len(animal_data)>0:
                for animal in animal_data:
                    cursor=self.__conn.cursor()
                    cursor.execute('SELECT COUNT(*) FROM animals WHERE terrain_id = ? AND name = ?',(region, animal))
                    inner_result=cursor.fetchone()[0]
                    summary+=(f"{inner_result} {animal}\n")
            else:
                summary=("Query returned no results.")
        except Exception as e:
            summary=("SQLite error:", e)
        return summary 



    def get_animals_all_regions(self):
        try:
            animal_data=self.load_json_data('animals.json')
            animal_names = []  
            for animal_name, animal_attributes in animal_data.items():
                animal_names.append(animal_name)
            db_connection.connection.execute('SELECT id FROM Terrain')
            results = db_connection.connection.fetchall()
            for result in results:
                result=result[0]
                print(result)
                if result:
                    for animal in animal_data:
                        cursor=sqlite3.connect('animal_database.db').cursor(0)
                        cursor.execute('SELECT COUNT(*) FROM animals WHERE terrain_id = ? AND name = ?',(str(result), animal))
                        inner_result=db_connection.connection.fetchone()[0]
                        print(f"There are {inner_result} {animal}")
                else:
                    print("Query returned no results.")
        except Exception as e:
            print("SQLite error:", e)
        finally:
            db_connection.connection.close()
            print("Database connection closed.")
