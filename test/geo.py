from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


def get_location_by_coordinates(latitude, longitude):
    """
    根据经纬度获取城市和国家信息
    """
    # 初始化地理编码器，需提供一个自定义的 user_agent
    geolocator = Nominatim(user_agent="geo_locator_app")

    try:
        # 反向地理编码：经纬度 -> 地址
        location = geolocator.reverse((latitude, longitude), language='en')

        if location:
            address = location.raw['address']
            city = address.get('city') or address.get('town') or address.get('village')
            country = address.get('country')
            return {
                'city': city,
                'country': country,
                'full_address': location.address
            }
        else:
            return {'error': 'No location found for the given coordinates.'}

    except GeocoderTimedOut:
        return {'error': 'Geocoder service timed out.'}
    except GeocoderServiceError as e:
        return {'error': f'Geocoder service error: {e}'}
    except Exception as e:
        return {'error': f'An unexpected error occurred: {e}'}


# 示例使用
if __name__ == "__main__":
    lat = 40.7128  # 纽约市纬度
    lon = -74.0060  # 纽约市经度

    result = get_location_by_coordinates(lat, lon)
    print(result)
