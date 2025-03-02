import geocoder
import time_disp

def device_location():
    try:
        g = geocoder.ip('me')  # 'me' refers to the current machine's IP
        if g.latlng:
            latitude, longitude = g.latlng
            cdt=str(latitude)+","+str(longitude)
            return cdt
        else:
            print("Could not retrieve location.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    device_location()