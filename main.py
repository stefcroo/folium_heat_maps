import folium
from folium.plugins import HeatMap


def generate_heat_map(df, df2, date, colorGradient, colorGradient2):
    location=[53.2194, 6.7563]
    df = df.loc[df.dates<=date]
    df2 = df2.loc[df2.dates<=date]
    print(df.head(20))
    # Starting point of the map
    heat_map = folium.Map(location=location, tiles = 'CartoDB positron', zoom_start=9) 
    # save all lat and lon and rescaled magnitudes to list values 
    latlons2 = df2[['lat', 'lon']].values.tolist()
    HeatMap(latlons2, gradient=colorGradient2,min_opacity=.7, blur=1, radius=2).add_to(heat_map)
    latlonsmag = df[['lat', 'lon','mag_rescale']].values.tolist()
    HeatMap(latlonsmag, gradient=colorGradient, min_opacity=0.8, radius=12, blur=20).add_to(heat_map)

    provinces = 'data/provincies/B1_Provinciegrenzen_van_NederlandPolygon.shp'
    fields = 'data/jan-2022-nlog-fields_utm/jan-2022-NLOG-Fields_UTM.shp'
    heat_map = add_provinces(provinces,heat_map)
    heat_map = add_fields(fields, heat_map)
    #add color legend to heatmap
    # linear = cmp.LinearColormap(['blue', 'cyan', 'lime', 'yellow', 'red'], vmin=-1, vmax=6, caption = 'Earthquakes in NL')
    # linear.add_to(heat_map)

    heat_map.save(f'earthquakes_{date}.html')
    time.sleep(1)
    save_png(date)

def save_png(date):
    driver = launchBrowser(date)
    driver.maximize_window()
    time.sleep(1)
    string = str(date)[:10]
    filename= f'output_date_{string}.png'
    png = driver.save_screenshot(filename)
    driver.quit()
    add_text(filename, date)

def launchBrowser(date):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--incognito")
    chrome_options.add_experimental_option("prefs", {"download.default_directory":os.getcwd()})
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)
    driver.get(f'file:///Users/StefanC/Desktop/Projects/api_earthquakes/earthquakes_{date}.html')
    time.sleep(1)
    return driver

def add_provinces(filename, map):
    gdf= gpd.read_file(filename)
    gdf.to_crs(epsg=4326)
    geometry = gdf.geometry
    gdf = GeoDataFrame(gdf, geometry=geometry)
    groningen = gdf.loc[gdf['PROV_NAAM'] =='Groningen']            
    folium.Choropleth(geo_data = groningen, data =geometry,fill_opacity=0).add_to(map)
    return map

def add_fields(filename, map):
    fields= gpd.read_file(filename)
    fields.to_crs(epsg=4326)
    geometry = fields.geometry
    fields = GeoDataFrame(fields, geometry=geometry)
    folium.Choropleth(geo_data = fields, data=geometry, fill_opacity=0.05, line_color = '#a9abaa', line_opacity = 1).add_to(map)
    return map


def add_text(filename,date):
    img = cv2.imread(filename)
    string = str(date)[:10]
    font                   = cv2.FONT_HERSHEY_TRIPLEX
    bottomLeftCornerOfText = (100,100)
    fontScale              = 3
    fontColor              = (0,0,0)
    thickness              = 3
    lineType               = 2
    cv2.putText(img,f"{string}", 
    bottomLeftCornerOfText, 
    font, 
    fontScale,
    fontColor,
    thickness,
    lineType)
    cv2.imwrite(f"{string}.jpg", img)

def create_video():
    image_folder = os.getcwd()
    video_name = 'earthquakes2000-2021.avi'
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
    images.sort()
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape
    video = cv2.VideoWriter(video_name, 0, 8, (width,height))
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))
    cv2.destroyAllWindows()
    video.release()

df = read_main_df('df_earthquakes.csv','2000-01-01')
df2 = read_second_df('boreholes.xlsx')

colorGradient = {0.0:'blue',
                0.25:'cyan',
                0.5:'lime',
                0.75:'yellow',
                1.0:'red'}
colorGradient2 = {0.0:'grey',
                1.0:'grey'}

dates = df.dates.unique()
dates.sort()
print(dates)
start_date = str(dates[0])[:10]
stop_date = str(dates[-1])[:10]
start = datetime.strptime(start_date, "%Y-%m-%d")
stop = datetime.strptime(stop_date, "%Y-%m-%d")
while start < stop:
    generate_heat_map(df, df2, start, colorGradient,colorGradient2)
    start = start + relativedelta(months=+1)
create_video()
